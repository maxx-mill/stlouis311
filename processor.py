"""
Data processor module for St. Louis 311 Service Integration.
Handles data cleaning, validation, and enrichment of raw API data.
"""

from datetime import datetime
from config import (
    DATE_FIELDS, DATE_FORMATS, COORDINATE_RANGES
)


class DataProcessor:
    """
    Professional data processor for St. Louis 311 service requests.
    Handles data cleaning, validation, and enrichment.
    """
    
    def __init__(self, api_client=None):
        self.api_client = api_client
    
    def process_and_validate_data(self, raw_requests):
        """
        Clean and validate data - critical professional step.
        Real-world APIs often have inconsistent or missing data.
        """
        processed_requests = []
        validation_stats = {
            'total': len(raw_requests),
            'valid_coordinates': 0,
            'missing_coordinates': 0,
            'invalid_dates': 0,
            'processed': 0
        }
        
        # Debug: Print the first few raw requests to see the structure
        if raw_requests:
            print("Sample raw API response structure:")
            sample_request = raw_requests[0]
            print(f"Available fields: {list(sample_request.keys())}")
            print(f"Sample request data: {sample_request}")
            
            # Print a few more samples to see variations
            for i, request in enumerate(raw_requests[:3]):
                print(f"Request {i+1} fields: {list(request.keys())}")
                print(f"Request {i+1} values: {request}")
                
            # Print all unique field names across all requests
            all_fields = set()
            for request in raw_requests:
                all_fields.update(request.keys())
            print(f"All unique fields found in API response: {sorted(list(all_fields))}")
            
            # Print a sample of non-empty values to see what data is actually available
            print("Sample of non-empty values from first few requests:")
            for i, request in enumerate(raw_requests[:5]):
                non_empty = {k: v for k, v in request.items() if v and str(v).strip()}
                print(f"Request {i+1} non-empty fields: {non_empty}")
        
        for request in raw_requests:
            try:
                # Professional data validation
                processed_request = {}
                
                # Handle coordinate extraction (critical for GIS)
                if not self._extract_coordinates(request, processed_request, validation_stats):
                    continue
                
                # Process dates with professional error handling
                self._process_dates(request, processed_request, validation_stats)
             
                # Copy other fields with data cleaning
                self._copy_and_clean_fields(request, processed_request)
                
                processed_requests.append(processed_request)
                validation_stats['processed'] += 1
                
            except Exception as e:
                print(f"Error processing request {request.get('service_request_id', 'unknown')}: {e}")
                continue
        
        # Print validation statistics (professional reporting)
        print(f"Data validation complete: {validation_stats}")
        return processed_requests
    
    def _extract_coordinates(self, request, processed_request, validation_stats):
        """
        Extract coordinates from known fields.
        Stores coordinates directly since geodatabase is in WGS84.
        """
        try:
            # Get coordinates from known fields (SRX/SRY or LAT/LONG)
            srx_raw = request.get('SRX')
            sry_raw = request.get('SRY')
            lat_raw = request.get('LAT')
            long_raw = request.get('LONG')
            
            # Try SRX/SRY first, then LAT/LONG
            x_coord = None
            y_coord = None
            
            if srx_raw and sry_raw:
                try:
                    x_coord = float(srx_raw)
                    y_coord = float(sry_raw)
                except (ValueError, TypeError):
                    pass
            
            if (x_coord is None or y_coord is None or x_coord == 0 or y_coord == 0) and (lat_raw and long_raw):
                try:
                    x_coord = float(lat_raw)
                    y_coord = float(long_raw)
                except (ValueError, TypeError):
                    pass
            
            # If we have valid coordinates, store them directly (geodatabase will be in WGS84)
            if x_coord is not None and y_coord is not None and x_coord != 0 and y_coord != 0:
                # Store the coordinates directly - the geodatabase is already in WGS84
                processed_request['SRX'] = x_coord  # Longitude
                processed_request['SRY'] = y_coord  # Latitude
                
                validation_stats['valid_coordinates'] += 1
                return True
            else:
                print(f"No valid coordinates found for request {request.get('SERVICE_REQUEST_ID')}")
                validation_stats['missing_coordinates'] += 1
                return False
                
        except Exception as e:
            print(f"Error processing coordinates for request {request.get('SERVICE_REQUEST_ID')}: {e}")
            validation_stats['missing_coordinates'] += 1
            return False
    
    def _process_dates(self, request, processed_request, validation_stats):
        """
        Process date fields with multiple format support.
        """
        # Map API date fields to our schema date fields
        date_field_mapping = {
            'REQUESTED_DATETIME': 'DATETIMEINIT',
            'UPDATED_DATETIME': 'DATETIMECLOSED',
            'EXPECTED_DATETIME': 'PRJCOMPLETEDATE'
        }
        
        for api_field, schema_field in date_field_mapping.items():
            date_str = request.get(api_field)
            if date_str:
                try:
                    # Handle ISO datetime format (2025-07-05T23:48:01Z)
                    if 'T' in date_str and ('Z' in date_str or '+' in date_str):
                        # Parse ISO datetime string
                        from datetime import datetime
                        # Remove 'Z' and parse as UTC
                        if date_str.endswith('Z'):
                            date_str = date_str[:-1]
                        processed_request[schema_field] = datetime.fromisoformat(date_str)
                    else:
                        # Handle multiple date formats (professional requirement)
                        for fmt in DATE_FORMATS:
                            try:
                                processed_request[schema_field] = datetime.strptime(date_str, fmt)
                                break
                            except ValueError:
                                continue
                except Exception as e:
                    print(f"Error processing date field {api_field} -> {schema_field}: {e}")
                    validation_stats['invalid_dates'] += 1
    
    def _copy_and_clean_fields(self, request, processed_request):
        """
        Copy and clean fields from raw request to processed request.
        Map API field names to our schema field names.
        """
        # Map API field names to our schema field names
        field_mapping = {
            'SERVICE_NAME': 'DESCRIPTION',
            'SERVICE_CODE': 'PROBLEMCODE',
            'ZIPCODE': 'PROBZIP',
            'ADDRESS': 'PROBADDRESS',
            'AGENCY_RESPONSIBLE': 'SUBMITTO',
            'STATUS': 'STATUS',
            'STATUS_NOTES': 'EXPLANATION',
            'SERVICE_NOTICE': 'CALLERTYPE',
            'MEDIA_URL': 'GROUP_'
        }
        
        # Initialize all schema fields with None/empty values
        schema_fields = [
            'CALLERTYPE', 'DATECANCELLED', 'DATEINVTDONE', 'DATETIMECLOSED', 
            'DATETIMEINIT', 'DESCRIPTION', 'EXPLANATION', 'NEIGHBORHOOD',
            'PLAIN_ENGLISH_NAME_FOR_PROBLEMCODE', 'PRJCOMPLETEDATE', 'PROBADDRESS',
            'PROBADDTYPE', 'PROBCITY', 'PROBLEMCODE', 'PROBZIP', 'REQUESTID',
            'STATUS', 'SUBMITTO', 'WARD', 'GROUP_'
        ]
        
        for field in schema_fields:
            processed_request[field] = None
        
        # Copy and map fields from API response (excluding date fields which are handled separately)
        for api_field, schema_field in field_mapping.items():
            value = request.get(api_field)
            
            if value is not None:
                # Type enforcement for integer fields
                if schema_field in ['REQUESTID', 'NEIGHBORHOOD', 'WARD', 'PROBZIP', 'PROBLEMCODE']:
                    try:
                        value = int(value) if value else None
                    except (ValueError, TypeError):
                        value = None
                elif isinstance(value, str):
                    value = value.strip()[:255]  # Truncate for TEXT fields
                
                processed_request[schema_field] = value
        
        # Handle special cases
        # REQUESTID - use SERVICE_REQUEST_ID if available, otherwise generate from SERVICE_CODE
        request_id = request.get('SERVICE_REQUEST_ID')
        if request_id:
            try:
                processed_request['REQUESTID'] = int(request_id)
            except (ValueError, TypeError):
                processed_request['REQUESTID'] = None
        else:
            # Generate a request ID from service code and timestamp if needed
            service_code = request.get('SERVICE_CODE')
            if service_code:
                processed_request['REQUESTID'] = service_code
        
        # NEIGHBORHOOD - might be in ADDRESS field or separate field
        if not processed_request['NEIGHBORHOOD']:
            address = request.get('ADDRESS', '')
            if address and ',' in address:
                # Try to extract neighborhood from address
                parts = address.split(',')
                if len(parts) > 1:
                    processed_request['NEIGHBORHOOD'] = parts[1].strip()
        
        # WARD - might be in ADDRESS field or separate field
        if not processed_request['WARD']:
            address = request.get('ADDRESS', '')
            if address and 'WARD' in address.upper():
                # Try to extract ward from address
                import re
                ward_match = re.search(r'WARD\s*(\d+)', address.upper())
                if ward_match:
                    try:
                        processed_request['WARD'] = int(ward_match.group(1))
                    except (ValueError, TypeError):
                        pass
        
        # PROBCITY - default to St. Louis
        if not processed_request['PROBCITY']:
            processed_request['PROBCITY'] = 'St. Louis'
        
        # PROBADDTYPE - default based on address type
        if not processed_request['PROBADDTYPE']:
            address = request.get('ADDRESS', '')
            if address:
                if any(word in address.upper() for word in ['STREET', 'AVE', 'BLVD', 'DR']):
                    processed_request['PROBADDTYPE'] = 'Street'
                elif any(word in address.upper() for word in ['ALLEY', 'LANE']):
                    processed_request['PROBADDTYPE'] = 'Alley'
                else:
                    processed_request['PROBADDTYPE'] = 'Address'
        
        # DATECANCELLED and DATEINVTDONE - not available in API, leave as None
        # PLAIN_ENGLISH_NAME_FOR_PROBLEMCODE - not available in API, leave as None
    
    def get_validation_summary(self, processed_requests):
        """
        Get a summary of data validation results.
        """
        total_requests = len(processed_requests)
        requests_with_coordinates = sum(1 for r in processed_requests if r.get('SRX') and r.get('SRY'))
        requests_with_dates = sum(1 for r in processed_requests if r.get('DATETIMEINIT'))
        overdue_requests = sum(1 for r in processed_requests if r.get('IS_OVERDUE') == 'Yes')
        
        return {
            'total_processed': total_requests,
            'with_coordinates': requests_with_coordinates,
            'with_dates': requests_with_dates,
            'overdue': overdue_requests,
            'coordinate_percentage': (requests_with_coordinates / total_requests * 100) if total_requests > 0 else 0
        } 