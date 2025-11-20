import os
import re
import requests
from datetime import datetime
from os.path import isfile
import json
import glob
import pandas as pd
from urllib.parse import quote
from fhirpathpy import evaluate
from utils import get_config
import logging

logger = logging.getLogger(__name__)

def run_capability_test(endpoint):
    """
       Fetch the capability statement from the endpoint and assert it 
       instantiates http://hl7.org/fhir/CapabilityStatement/terminology-server
    """
    query = f'{endpoint}/metadata'
    headers = {'Accept': 'application/fhir+json'}
    response = requests.get(query, headers=headers)
    if response.status_code == 200:
        data = response.json()
        server_type = evaluate(data, "instantiates[0]")
        fhir_version = evaluate(data, "fhirVersion")
        if (isinstance(server_type, list) and len(server_type) > 0 and 
            server_type[0] == "http://hl7.org/fhir/CapabilityStatement/terminology-server" and 
            isinstance(fhir_version, list) and len(fhir_version) > 0 and 
            fhir_version[0] == "4.0.1"):
            return 200  # OK
        else:
            return 418  # I'm a teapot (have we upgraded to a new version??)
    else:
        return response.status_code   # I'm most likely offline


def run_terminology_mapper(endpoint, sct_edition, sct_version, outdir):
    """
    Reads a spreadsheet of LOINC codes and outputs a map to SNOMED (using LOINCSNOMED extension)

    Args:
        endpoint (str): Base URL of the FHIR terminology server.
        sct_edition (str): SNOMED CT edition ID.
        sct_version (str): SNOMED CT version date.
        outdir (str): Directory to save the map files.

    Returns:
        str: Path to the map file, or None if an error occurred.
    """
    now = datetime.now() # current date and time
    ts = now.strftime("%Y%m%d-%H%M%S")    

    logger.info(f"Starting terminology mapping against: {endpoint}")
    output_file = os.path.join(outdir, f'snomed-loinc-map-{sct_version}.tsv')
    
    # Step 0: Check if a map exists for this sct version; if it exists, skip recreating that file
    if os.path.isfile(output_file):
        logger.info(f"Map file already exists for version {sct_version}: {output_file}")
        logger.info("Skipping map generation. Delete the file to regenerate.")
        return output_file

    # Step 1: Get observables dataframe from SNOMED CT ECL
    logger.info("Step 1: Fetching Observable entities from SNOMED CT using ECL")
    
    # ECL expression to get all Non functional / exam Observable entities
    ecl = "( < 363787002 ) MINUS ( (<< 78064003 OR << 246464006 OR << 363788007 ) )"
    # Smaller test : 1405 concepts using descendants of 32337-8 Protein [Mass/volume] in Specimen
    # ecl = "<< 177301010000109"
    ecl_encoded = quote(ecl, safe='')
    valueset_url = f"http://snomed.info/sct/{sct_edition}/version/{sct_version}?fhir_vs=ecl/{ecl_encoded}"
    
    expand_query = f'{endpoint}/ValueSet/$expand?url={quote(valueset_url, safe="")}'
    headers = {'Accept': 'application/fhir+json'}
    
    logger.info(f"Expanding ValueSet with ECL: {ecl}")
    response = requests.get(expand_query, headers=headers)
    
    if response.status_code != 200:
        logger.error(f"Failed to expand ValueSet: {response.status_code}")
        logger.error(f"Response: {response.text}")
        return None
    
    expansion_data = response.json()
    
    # Extract concepts from expansion
    concepts = []
    if 'expansion' in expansion_data and 'contains' in expansion_data['expansion']:
        for concept in expansion_data['expansion']['contains']:
            concepts.append({
                'code': concept.get('code'),
                'display': concept.get('display')
            })
    
    logger.info(f"Found {len(concepts)} Observable entity concepts")
    
    # Create pandas dataframe
    obsdata = pd.DataFrame(concepts)
    
    # Step 2: Iterate through concepts and lookup properties to find LOINC mappings
    logger.info("Step 2: Looking up properties for each concept to find LOINC mappings")
    
    loinc_codes = []
    
    for count, (idx, row) in enumerate(obsdata.iterrows(), start=1):
        code = row['code']
        display = row['display']
        
        # Lookup properties for this concept
        lookup_query = (f'{endpoint}/CodeSystem/$lookup?'
                       f'version=http://snomed.info/sct/{sct_edition}/version/{sct_version}&'
                       f'code={code}&'
                       f'property=*&'
                       f'system=http://snomed.info/sct')
        
        logger.info(f"Looking up properties for {code} - {display} ({count}/{len(obsdata)})")
        
        try:
            lookup_response = requests.get(lookup_query, headers=headers)
            
            if lookup_response.status_code == 200:
                lookup_data = lookup_response.json()
                
                # Find equivalentConcept property
                loinc_code = ""
                if 'parameter' in lookup_data:
                    for param in lookup_data['parameter']:
                        if param.get('name') == 'property':
                            parts = param.get('part', [])
                            # Check if this is the equivalentConcept property
                            code_part = None
                            value_part = None
                            
                            for part in parts:
                                if part.get('name') == 'code' and part.get('valueCode') == 'equivalentConcept':
                                    code_part = part
                                elif part.get('name') == 'value' and 'valueCoding' in part:
                                    value_part = part
                            
                            if code_part and value_part:
                                coding = value_part.get('valueCoding', {})
                                if coding.get('system') == 'http://loinc.org':
                                    loinc_code = coding.get('code', '')
                                    break
                
                loinc_codes.append(loinc_code)
            else:
                logger.warning(f"Failed to lookup properties for {code}: {lookup_response.status_code}")
                loinc_codes.append("")
        except Exception as e:
            logger.error(f"Error looking up {code}: {str(e)}")
            loinc_codes.append("")
    
    # Add LOINC codes to dataframe
    obsdata['loinc_code'] = loinc_codes
    
    # Step 3: Output to TSV file
    logger.info("Step 3: Writing results to TSV file")
    
    obsdata.to_csv(output_file, sep='\t', index=False)
    
    logger.info(f"Map file created: {output_file}")
    logger.info(f"Total concepts: {len(obsdata)}")
    logger.info(f"Concepts with LOINC mapping: {obsdata['loinc_code'].astype(bool).sum()}")
    
    return output_file


def map_to_rcpa_spia(spia_file, map_file, outdir):
    """
    This function imports a SPIA Lab results spreadsheet and adds a SNOMED CT column to the end.
    Use the map_file column labeled "loinc_code" to lookup the equivalent SNOMED CT concept 
    using the column matching "LOINC" in row 1 of the SPIA Spreadsheet.
    Create a new spreadsheet that includes the SNOMED CT equivalent concept id and the 
    SNOMED CT preferred term from column 2 of the map file.
    
    Args:
        spia_file (str): Path to the SPIA Lab results spreadsheet.
        map_file (str): Path to the SNOMED-LOINC map TSV file.
        outdir (str): Directory to save the output file.
    
    Returns:
        str: Path to the output file, or None if an error occurred.
    """
    # Check if openpyxl is available for Excel file support
    try:
        import openpyxl
    except ImportError:
        logger.error("openpyxl is not installed. Please install it with: pip install openpyxl")
        return None
    
    logger.info(f"Starting SPIA to SNOMED CT mapping")
    logger.info(f"SPIA file: {spia_file}")
    logger.info(f"Map file: {map_file}")
    
    try:
        # Read the SPIA spreadsheet
        logger.info("Reading SPIA spreadsheet...")
        
        # Determine file type and read accordingly
        file_extension = os.path.splitext(spia_file)[1].lower()
        
        # For Excel files, first check which sheets are available
        if file_extension in ['.xlsx', '.xls']:
            import openpyxl
            xl_file = pd.ExcelFile(spia_file, engine='openpyxl' if file_extension == '.xlsx' else None)
            logger.info(f"Excel file contains sheets: {', '.join(str(s) for s in xl_file.sheet_names)}")
            
            # Try to find the sheet with data (usually not the first if there's a cover sheet)
            sheet_to_use = None
            for sheet_name in xl_file.sheet_names:
                logger.info(f"Checking sheet: {sheet_name}")
                temp_df = pd.read_excel(spia_file, sheet_name=sheet_name, engine='openpyxl' if file_extension == '.xlsx' else None, nrows=5)
                logger.info(f"  First few columns: {', '.join(str(c) for c in temp_df.columns[:5])}")
                
                # Check if this sheet has a LOINC column in first 2 rows
                for col in temp_df.columns:
                    if str(col).strip().upper() == 'LOINC':
                        sheet_to_use = sheet_name
                        logger.info(f"  Found LOINC column in sheet: {sheet_name}")
                        break
                
                if sheet_to_use:
                    break
            
            if not sheet_to_use:
                # Default to first sheet and try different header rows
                sheet_to_use = xl_file.sheet_names[0]
                logger.warning(f"LOINC column not found in default position. Using sheet: {sheet_to_use}")
        
        # Try reading with different header rows (0, 1, 2)
        loinc_column_name = None
        for header_row in [0, 1, 2]:
            if file_extension in ['.xlsx', '.xls']:
                spia_df = pd.read_excel(spia_file, sheet_name=sheet_to_use, engine='openpyxl' if file_extension == '.xlsx' else None, header=header_row)
            elif file_extension == '.tsv':
                spia_df = pd.read_csv(spia_file, sep='\t', header=header_row)
            elif file_extension == '.csv':
                spia_df = pd.read_csv(spia_file, header=header_row)
            else:
                logger.error(f"Unsupported file format: {file_extension}")
                return None
            
            logger.info(f"Trying header row {header_row + 1}. Columns: {', '.join(str(c) for c in spia_df.columns[:10])}")
            
            # Check if LOINC column exists (case-insensitive search)
            for col in spia_df.columns:
                if str(col).strip().upper() == 'LOINC':
                    loinc_column_name = col
                    logger.info(f"Found '{col}' column in row {header_row + 1}")
                    break
            
            if loinc_column_name:
                break
            elif header_row < 2:
                logger.warning(f"'LOINC' column not found in row {header_row + 1}. Trying row {header_row + 2} as header...")
        else:
            # Loop completed without finding LOINC column
            logger.error(f"Error: SPIA file does not contain a 'LOINC' column in rows 1-3")
            logger.error(f"Last attempt columns: {', '.join(str(c) for c in spia_df.columns)}")
            return None
        
        logger.info(f"Found {len(spia_df)} rows in SPIA file")
        
        # Read the map file
        logger.info("Reading SNOMED-LOINC map file...")
        map_df = pd.read_csv(map_file, sep='\t')
        
        # Verify map file has required columns
        if 'loinc_code' not in map_df.columns or 'code' not in map_df.columns or 'display' not in map_df.columns:
            logger.error(f"Error: Map file missing required columns (loinc_code, code, display)")
            logger.error(f"Available columns: {', '.join(map_df.columns)}")
            return None
        
        logger.info(f"Map file contains {len(map_df)} SNOMED CT concepts")
        
        # Create a lookup dictionary from LOINC code to SNOMED CT code and display
        # Only include entries where loinc_code is not empty
        loinc_to_snomed = {}
        for _, row in map_df.iterrows():
            loinc_code = row['loinc_code']
            if pd.notna(loinc_code) and loinc_code != '':
                loinc_to_snomed[str(loinc_code).strip()] = {
                    'snomed_code': row['code'],
                    'snomed_display': row['display']
                }
        
        logger.info(f"Created lookup table with {len(loinc_to_snomed)} LOINC to SNOMED mappings")
        
        # Map LOINC codes to SNOMED CT codes using vectorized operations
        logger.info("Mapping LOINC codes to SNOMED CT...")
        
        # Clean and normalize LOINC codes
        spia_df['_loinc_clean'] = spia_df[loinc_column_name].astype(str).str.strip()
        
        # Use map() for vectorized lookup - much faster than iterrows()
        spia_df['SNOMED_CT_Code'] = spia_df['_loinc_clean'].map(
            lambda x: loinc_to_snomed.get(x, {}).get('snomed_code', '') if x and x != 'nan' else ''
        )
        spia_df['SNOMED_CT_Display'] = spia_df['_loinc_clean'].map(
            lambda x: loinc_to_snomed.get(x, {}).get('snomed_display', '') if x and x != 'nan' else ''
        )
        
        # Remove temporary column
        spia_df.drop(columns=['_loinc_clean'], inplace=True)
        
        # Count mappings
        mapped_count = (spia_df['SNOMED_CT_Code'] != '').sum()
        unmapped_count = len(spia_df) - mapped_count
        logger.info(f"Successfully mapped {mapped_count} out of {len(spia_df)} rows to SNOMED CT")
        
        # Generate output filename
        now = datetime.now()
        ts = now.strftime("%Y%m%d-%H%M%S")
        base_name = os.path.splitext(os.path.basename(spia_file))[0]
        output_file = os.path.join(outdir, f'{base_name}-snomed-mapped-{ts}.xlsx')
        
        # Write output file
        logger.info(f"Writing output file: {output_file}")
        spia_df.to_excel(output_file, index=False)
        
        logger.info(f"SPIA mapping completed successfully")
        logger.info(f"Output file: {output_file}")
        
        # Log summary
        logger.info("=" * 80)
        logger.info(f"MAPPING SUMMARY")
        logger.info(f"File: {os.path.basename(spia_file)}")
        logger.info(f"MAPPED: {mapped_count}")
        logger.info(f"UNMAPPED: {unmapped_count}")
        logger.info(f"TOTAL: {len(spia_df)}")
        logger.info("=" * 80)
        
        return output_file
        
    except FileNotFoundError as e:
        logger.error(f"Error: File not found - {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error processing SPIA file: {str(e)}")
        return None



