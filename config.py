"""
Configuration settings for St. Louis 311 Service Integration.
Centralized configuration management for professional GIS applications.
"""

import os
from datetime import datetime, timedelta

# API Configuration
API_KEY = "MTc1MTQ3MjkxMDMwMDAuMjgwNDAwMDQ5OTg5"  # Request from St. Louis IT
API_BASE_URL = "https://www.stlouis-mo.gov/powernap/stlouis/api.cfm"
BASE_URL = "https://www.stlouis-mo.gov/powernap/stlouis/api.cfm/requests.json"

# Date Range Configuration
START_DATE = datetime.now() - timedelta(days=1)  # Yesterday
END_DATE = datetime.now()                        # Today (inclusive)

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
GEODATABASE_PATH = r"C:\Users\mills\geo_dev\stlouis311\StLouis311.gdb"
COORDINATE_SYSTEM = "EPSG:4326"  # WGS84 Geographic

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