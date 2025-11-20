import requests
import logging
from map import run_capability_test

# Setup logging
logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def test_snomed_to_loinc_mapping(endpoint, sct_edition, sct_version):
    """
    Test SNOMED CT to LOINC mapping using the terminology server.
    
    Tests:
    1. SNOMED CT code '168331010000106' should map to LOINC "718-7"
    2. SNOMED CT code '77386006' should have no LOINC mapping
    
    Args:
        endpoint (str): Base URL of the FHIR terminology server.
        sct_edition (str): SNOMED CT edition ID.
        sct_version (str): SNOMED CT version date.
    
    Returns:
        bool: True if all tests pass, False otherwise.
    """
    headers = {'Accept': 'application/fhir+json'}
    all_tests_passed = True
    
    # Test 1: SNOMED CT '168331010000106' should map to LOINC "718-7"
    logger.info("=" * 80)
    logger.info("Test 1: Checking SNOMED CT '168331010000106' maps to LOINC '718-7'")
    logger.info("=" * 80)
    
    code1 = '168331010000106'
    expected_loinc1 = '718-7'
    
    lookup_query1 = (f'{endpoint}/CodeSystem/$lookup?'
                    f'version=http://snomed.info/sct/{sct_edition}/version/{sct_version}&'
                    f'code={code1}&'
                    f'property=*&'
                    f'system=http://snomed.info/sct')
    
    try:
        response1 = requests.get(lookup_query1, headers=headers)
        
        if response1.status_code == 200:
            lookup_data1 = response1.json()
            
            # Find equivalentConcept property
            loinc_code1 = None
            display1 = None
            
            if 'parameter' in lookup_data1:
                for param in lookup_data1['parameter']:
                    # Get display name
                    if param.get('name') == 'display':
                        display1 = param.get('valueString', '')
                    
                    # Find LOINC mapping
                    if param.get('name') == 'property':
                        parts = param.get('part', [])
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
                                loinc_code1 = coding.get('code', '')
                                break
            
            logger.info(f"SNOMED CT Code: {code1}")
            logger.info(f"Display: {display1}")
            logger.info(f"Found LOINC: {loinc_code1}")
            logger.info(f"Expected LOINC: {expected_loinc1}")
            
            if loinc_code1 == expected_loinc1:
                logger.info("✅ TEST 1 PASSED: Correct LOINC mapping found")
            else:
                logger.error(f"❌ TEST 1 FAILED: Expected '{expected_loinc1}' but got '{loinc_code1}'")
                all_tests_passed = False
        else:
            logger.error(f"❌ TEST 1 FAILED: HTTP {response1.status_code} - {response1.text}")
            all_tests_passed = False
    except Exception as e:
        logger.error(f"❌ TEST 1 FAILED: Exception - {str(e)}")
        all_tests_passed = False
    
    # Test 2: SNOMED CT '77386006' should have NO LOINC mapping
    logger.info("")
    logger.info("=" * 80)
    logger.info("Test 2: Checking SNOMED CT '77386006' has NO LOINC mapping")
    logger.info("=" * 80)
    
    code2 = '77386006'
    
    lookup_query2 = (f'{endpoint}/CodeSystem/$lookup?'
                    f'version=http://snomed.info/sct/{sct_edition}/version/{sct_version}&'
                    f'code={code2}&'
                    f'property=*&'
                    f'system=http://snomed.info/sct')
    
    try:
        response2 = requests.get(lookup_query2, headers=headers)
        
        if response2.status_code == 200:
            lookup_data2 = response2.json()
            
            # Find equivalentConcept property
            loinc_code2 = None
            display2 = None
            
            if 'parameter' in lookup_data2:
                for param in lookup_data2['parameter']:
                    # Get display name
                    if param.get('name') == 'display':
                        display2 = param.get('valueString', '')
                    
                    # Find LOINC mapping
                    if param.get('name') == 'property':
                        parts = param.get('part', [])
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
                                loinc_code2 = coding.get('code', '')
                                break
            
            logger.info(f"SNOMED CT Code: {code2}")
            logger.info(f"Display: {display2}")
            logger.info(f"Found LOINC: {loinc_code2 if loinc_code2 else '(none)'}")
            
            if loinc_code2 is None or loinc_code2 == '':
                logger.info("✅ TEST 2 PASSED: No LOINC mapping found (as expected)")
            else:
                logger.error(f"❌ TEST 2 FAILED: Expected no LOINC mapping but found '{loinc_code2}'")
                all_tests_passed = False
        else:
            logger.error(f"❌ TEST 2 FAILED: HTTP {response2.status_code} - {response2.text}")
            all_tests_passed = False
    except Exception as e:
        logger.error(f"❌ TEST 2 FAILED: Exception - {str(e)}")
        all_tests_passed = False
    
    # Summary
    logger.info("")
    logger.info("=" * 80)
    if all_tests_passed:
        logger.info("✅ ALL TESTS PASSED")
    else:
        logger.error("❌ SOME TESTS FAILED")
    logger.info("=" * 80)
    
    return all_tests_passed


if __name__ == '__main__':
    # Default endpoint and SNOMED CT version
    endpoint = "http://localhost:8080/fhir"
    sct_edition = "11010000107"  # LOINC SNOMED extension
    sct_version = "20250921"     # Current Production version
    
    logger.info(f"Testing SNOMED to LOINC mapping against: {endpoint}")
    logger.info(f"SNOMED CT Edition: {sct_edition}")
    logger.info(f"SNOMED CT Version: {sct_version}")
    logger.info("")
    
    # First, test the capability statement
    logger.info("Checking terminology server capability...")
    capability_status = run_capability_test(endpoint)
    
    if capability_status == 200:
        logger.info("✅ Terminology server is ready")
        logger.info("")
        
        # Run the tests
        success = test_snomed_to_loinc_mapping(endpoint, sct_edition, sct_version)
        
        # Exit with appropriate code
        exit(0 if success else 1)
    else:
        logger.error(f"❌ Terminology server check failed with status: {capability_status}")
        logger.error("Please ensure the FHIR terminology server is running at the correct endpoint")
        exit(1)
