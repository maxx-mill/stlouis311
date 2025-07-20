"""
Enhanced configuration settings for St. Louis 311 Service Integration with ArcGIS Online.
Centralized configuration management for professional GIS applications.
"""

import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

API_KEY = os.environ.get("STL311_API_KEY")
if not API_KEY:
    print("Warning: STL311_API_KEY environment variable is not set. API requests may fail.")

API_BASE_URL = "https://www.stlouis-mo.gov/powernap/stlouis/api.cfm"
BASE_URL = "https://www.stlouis-mo.gov/powernap/stlouis/api.cfm/requests.json"

# Date Range Configuration
START_DATE = dt.now() - timedelta(days=1)  # Yesterday
END_DATE = dt.now()                        # Today (inclusive)

# API Request Configuration
DEFAULT_DAYS_BACK = 30
PAGE_SIZE = 1000
MAX_PAGES = 10  # Reduced for testing
MAX_RETRIES = 3
REQUEST_TIMEOUT = 30
RATE_LIMIT_DELAY = 1.0

# Status Configuration
DEFAULT_STATUS = "open"  # Simplified status for testing

# Geodatabase Configuration
GEODATABASE_PATH = os.path.join(os.path.dirname(__file__), "StLouis311.gdb") #relative path to the gdb
COORDINATE_SYSTEM = "EPSG:3857"  # Web Mercator

# Service Requests Schema (simplified for direct field mapping)
SERVICE_REQUESTS_SCHEMA = {
    'CALLERTYPE': 'TEXT',
    'DATECANCELLED': 'DATE',
    'DATEINVTDONE': 'DATE',
    'DATETIMECLOSED': 'DATE',
    'DATETIMEINIT': 'DATE',
    'DESCRIPTION': 'TEXT',
    'EXPLANATION': 'TEXT',
    'GROUP_': 'TEXT',  # ArcGIS renamed GROUP to GROUP_
    'NEIGHBORHOOD': 'LONG',
    'PLAIN_ENGLISH_NAME_FOR_PROBLEMCODE': 'TEXT',
    'PRJCOMPLETEDATE': 'DATE',
    'PROBADDRESS': 'TEXT',
    'PROBADDTYPE': 'TEXT',
    'PROBCITY': 'TEXT',
    'PROBLEMCODE': 'TEXT',
    'PROBZIP': 'LONG',
    'REQUESTID': 'LONG',
    'SRX': 'DOUBLE',  # Longitude (WGS84)
    'SRY': 'DOUBLE',  # Latitude (WGS84)
    'STATUS': 'TEXT',
    'SUBMITTO': 'TEXT',
    'WARD': 'LONG'
}

# Date Fields for Processing
DATE_FIELDS = ['DATETIMEINIT', 'DATETIMECLOSED', 'PRJCOMPLETEDATE', 'DATEINVTDONE', 'DATECANCELLED']

# Date Formats for Parsing
DATE_FORMATS = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%m/%d/%Y']


# Coordinate Validation Ranges (WGS84 Geographic - EPSG:4326)
# St. Louis area bounds in decimal degrees
COORDINATE_RANGES = {
    'min_x': -90.4,  # Longitude (West) - WGS84
    'max_x': -90.1,  # Longitude (East) - WGS84  
    'min_y': 38.5,   # Latitude (South) - WGS84
    'max_y': 38.8    # Latitude (North) - WGS84
} 

# ArcGIS Online Configuration
ARCGIS_ONLINE_CONFIG = {
    # Default service settings
    'default_service_name': 'StLouis311_ServiceRequests',
    'default_folder': 'StLouis311',
    'default_update_method': 'replace',  # 'replace', 'append', or 'incremental'
    
    # Service properties
    'service_properties': {
        'title': 'St. Louis 311 Service Requests',
        'description': 'Real-time 311 service requests for the City of St. Louis. Auto-updated from the St. Louis Open311 API.',
        'tags': ['311', 'St. Louis', 'service requests', 'government', 'open data', 'public services'],
        'snippet': 'Current 311 service requests for the City of St. Louis',
        'accessInformation': 'City of St. Louis Open Data Portal',
        'licenseInfo': 'Public Domain - City of St. Louis',
        'type': 'Feature Service'
    },
    
    # Publishing parameters
    'publish_parameters': {
        'hasStaticData': False,
        'maxRecordCount': 10000,
        'allowGeometryUpdates': True,
        'capabilities': 'Query,Create,Update,Delete,Uploads,Editing',
        'units': 'esriMeters',
        'xssPreventionEnabled': True,
        'enableZDefaults': False,
        'allowUpdateWithoutMValues': True
    },
    
    # Sharing settings
    'sharing': {
        'everyone': True,  # Share publicly
        'org': True,       # Share with organization
        'groups': []       # Specific groups (list of group IDs)
    },
    
    # Update settings
    'update_settings': {
        'chunk_size': 1000,  # Number of features to process at once
        'max_attempts': 3,   # Maximum retry attempts
        'retry_delay': 2,    # Seconds to wait between retries
        'timeout': 300       # Timeout for operations in seconds
    }
}

ARCGIS_OAUTH_CONFIG = {
    'portal_url': 'https://pennstate.maps.arcgis.com/'
    # All other OAuth-specific keys are removed as GIS("pro") handles authentication
}
