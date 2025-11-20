import requests
import logging
import pandas as pd
from urllib.parse import quote
from map import run_capability_test

# Setup logging
logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def test_ecl_expansion(endpoint, ecl, sct_edition=None, sct_version=None):
    """
    Test ECL expression expansion to see the format of the output.
    
    Args:
        endpoint (str): Base URL of the FHIR terminology server.
        ecl (str): ECL expression to expand.
        sct_edition (str, optional): SNOMED CT edition ID.
        sct_version (str, optional): SNOMED CT version date.
    
    Returns:
        pandas.DataFrame: DataFrame with the expanded concepts.
    """
    logger.info("=" * 80)
    logger.info(f"Testing ECL Expression: {ecl}")
    if sct_edition and sct_version:
        logger.info(f"SNOMED CT Edition: {sct_edition}")
        logger.info(f"SNOMED CT Version: {sct_version}")
    logger.info("=" * 80)
    
    # Encode the ECL expression
    ecl_encoded = quote(ecl, safe='')
    
    # Use versioned URL if edition and version are provided, otherwise use simple format
    if sct_edition and sct_version:
        valueset_url = f"http://snomed.info/sct/{sct_edition}/version/{sct_version}?fhir_vs=ecl/{ecl_encoded}"
    else:
        valueset_url = f"http://snomed.info/sct?fhir_vs=ecl/{ecl_encoded}"
    
    expand_query = f'{endpoint}/ValueSet/$expand?url={quote(valueset_url, safe="")}'
    headers = {'Accept': 'application/fhir+json'}
    
    logger.info(f"Expansion URL: {expand_query}")
    logger.info("")
    
    try:
        response = requests.get(expand_query, headers=headers)
        
        if response.status_code == 200:
            expansion_data = response.json()
            
            # Extract concepts from expansion
            concepts = []
            if 'expansion' in expansion_data and 'contains' in expansion_data['expansion']:
                for concept in expansion_data['expansion']['contains']:
                    concepts.append({
                        'code': concept.get('code'),
                        'display': concept.get('display'),
                        'system': concept.get('system', '')
                    })
            
            # Create pandas dataframe
            df = pd.DataFrame(concepts)
            
            logger.info(f"✅ Successfully expanded ECL expression")
            logger.info(f"Found {len(df)} concepts")
            logger.info("")
            logger.info("=" * 80)
            logger.info("EXPANSION RESULTS:")
            logger.info("=" * 80)
            
            # Display the dataframe
            if len(df) > 0:
                # Set pandas display options to show full content
                pd.set_option('display.max_rows', None)
                pd.set_option('display.max_columns', None)
                pd.set_option('display.width', None)
                pd.set_option('display.max_colwidth', None)
                
                print(df.to_string(index=True))
                
                logger.info("")
                logger.info("=" * 80)
                logger.info("SUMMARY:")
                logger.info("=" * 80)
                logger.info(f"Total concepts: {len(df)}")
                logger.info(f"Columns: {', '.join(df.columns)}")
                logger.info("")
                logger.info("First few rows in detail:")
                for count, (idx, row) in enumerate(df.head(5).iterrows(), start=1):
                    logger.info(f"\nConcept {count}:")
                    logger.info(f"  Code: {row['code']}")
                    logger.info(f"  Display: {row['display']}")
                    logger.info(f"  System: {row['system']}")
            else:
                logger.warning("No concepts found in expansion")
            
            return df
        else:
            logger.error(f"❌ Failed to expand ValueSet: HTTP {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
    except Exception as e:
        logger.error(f"❌ Exception occurred: {str(e)}")
        return None


if __name__ == '__main__':
    # Default endpoint
    endpoint = "http://localhost:8080/fhir"
    
    # ECL expression to test
    ecl = "<< 177301010000109"
    
    # SNOMED CT edition and version
    sct_edition = "11010000107"  # LOINC SNOMED extension
    sct_version = "20250921"     # Current Production version
    
    logger.info(f"Testing ECL expansion against: {endpoint}")
    logger.info("")
    
    # First, test the capability statement
    logger.info("Checking terminology server capability...")
    capability_status = run_capability_test(endpoint)
    
    if capability_status == 200:
        logger.info("✅ Terminology server is ready")
        logger.info("")
        
        # Run the ECL expansion test
        result_df = test_ecl_expansion(endpoint, ecl, sct_edition, sct_version)
        
        # Exit with appropriate code
        exit(0 if result_df is not None else 1)
    else:
        logger.error(f"❌ Terminology server check failed with status: {capability_status}")
        logger.error("Please ensure the FHIR terminology server is running at the correct endpoint")
        exit(1)
