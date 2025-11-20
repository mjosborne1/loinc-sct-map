import argparse
import os
import glob
from pathlib import Path
import logging
from datetime import datetime
from utils import check_path
from map import run_capability_test, run_terminology_mapper, map_to_rcpa_spia
    

def main():
    homedir = os.environ['HOME']
    parser = argparse.ArgumentParser(description='Create Observable to LOINC map file')
    defaultpath = os.path.join(homedir, "data", "loinc-sct-map")
    defaulttx = "http://localhost:8080/fhir"
    defaultedition = "11010000107"  #  LOINC SNOMED extension
    defaultversion = "20250921"     #  Current Production version
    logger = logging.getLogger(__name__)
    parser.add_argument("-r", "--rootdir", help="Root data folder", default=defaultpath)   
    parser.add_argument("-t", "--txendpoint", help="Terminology server endpoint", default=defaulttx)   
    parser.add_argument("-e", "--edition", help="SNOMED CT edition id", default=defaultedition)   
    parser.add_argument("-v", "--version", help="SNOMED CT version date (YYYYMMDD)", default=defaultversion)   
    args = parser.parse_args()
    
    ## Create the data path if it doesn't exist
    check_path(args.rootdir)

    # setup report output folder for TSV reports   
    outdir = os.path.join(args.rootdir, "maps")
    check_path(outdir)

    # setup input folder for Excel files to be mapped
    # Script assumes a column  
    indir = os.path.join(args.rootdir, "in")
    check_path(indir)
    
    # setup output folder for mapped Excel files
    out_dir = os.path.join(args.rootdir, "out")
    check_path(out_dir)
    
    # setup logs folder
    logs_dir = os.path.join(args.rootdir, "logs")
    check_path(logs_dir)

    ## Setup logging
    now = datetime.now() # current date and time
    ts = now.strftime("%Y%m%d-%H%M%S")
    FORMAT = '%(asctime)s %(lineno)d : %(message)s'
    logging.basicConfig(
        format=FORMAT, 
        filename=os.path.join(logs_dir, f'loinc-sct-map-{ts}.log'),
        level=logging.INFO
    )
    logger.info('Started mustSupport element extraction')
    run_capability_test(args.txendpoint)
    
    # Run SNOMED to LOINC mapper if the mapfile doesn't exist for this version
    map_file = run_terminology_mapper(args.txendpoint, args.edition, args.version, outdir)

    # Check if map file was created successfully
    if map_file is None:
        logger.error("Failed to create or locate SNOMED-LOINC map file. Exiting.")
        return
    
    # Run a lookup in the SPIA Lab result Spreadsheet files contained in indir
    logger.info(f"Searching for Excel files in: {indir}")
    
    # Find all .xlsx files in the input directory
    excel_files = glob.glob(os.path.join(indir, "*.xlsx"))
    
    if not excel_files:
        logger.warning(f"No Excel (.xlsx) files found in {indir}")
    else:
        logger.info(f"Found {len(excel_files)} Excel file(s) to process")
        
        for excel_file in excel_files:
            logger.info(f"Processing: {excel_file}")
            output_file = map_to_rcpa_spia(excel_file, map_file, out_dir)
            
            if output_file:
                logger.info(f"Successfully processed {os.path.basename(excel_file)}")
            else:
                logger.error(f"Failed to process {os.path.basename(excel_file)}")
    
    logger.info("Processing complete")

if __name__ == '__main__':
    main()