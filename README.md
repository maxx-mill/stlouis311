# St. Louis 311 Service Integration

A professional, modular Python integration system for St. Louis 311 service requests using ArcPy. This system fetches service requests from the St. Louis Open311 API, processes and validates the data, and stores it in a geodatabase.

## Features

- **Modular Architecture**: Clean separation of concerns with dedicated modules for API, processing, and geodatabase
- **Professional Data Processing**: Robust data validation, coordinate transformation, and error handling
- **ArcGIS Integration**: Native geodatabase support with proper coordinate systems
- **Comprehensive Logging**: Professional logging with configurable levels
- **Coordinate Transformation**: Automatic handling of Web Mercator (EPSG:3857) coordinates

## Project Structure

```
stlouis311/
├── main.py              # Main execution script
├── integration.py       # Integration orchestrator
├── api_client.py        # API client for St. Louis Open311
├── processor.py         # Data processing and validation
├── updater.py           # Geodatabase updates
├── geodatabase.py       # Geodatabase management

├── config.py            # Configuration settings
├── README.md            # This file
└── StLouis311.gdb/      # ArcGIS geodatabase
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd stlouis311
   ```

2. **Install Python dependencies**:
   ```bash
   pip install requests
   ```

3. **ArcGIS Pro**: Ensure ArcGIS Pro is installed with Python environment

## API Key Setup

This project requires an API key for the St. Louis 311 API. **Do not commit your API key to version control.**

1. Create a file named `.env` in the project root (this file is already in `.gitignore`).
2. Add your API key to the `.env` file:
   ```
   STL311_API_KEY=your_actual_api_key_here
   ```
3. The application will automatically load this key using `python-dotenv`.

## Configuration (updated)

Edit `config.py` to configure:

- **API Key**: Loaded from the environment variable `STL311_API_KEY` (see above)
- **API Settings**: API base URL, request parameters
- **Date Range**: Default date range for data fetching
- **Geodatabase**: Path and coordinate system settings
- **Logging**: Log level and file settings

## Usage

### Basic Integration

Run the complete integration workflow:

```bash
python main.py
```

This will:
1. Fetch service requests from the St. Louis Open311 API
2. Process and validate the data
3. Handle coordinates as Web Mercator (EPSG:3857) X/Y meters
4. Store results in the geodatabase

### Individual Components

You can also use individual components:

```python
from api_client import APIClient
from processor import DataProcessor
from updater import DataUpdater

# Fetch data
api_client = APIClient()
raw_requests = api_client.fetch_service_requests()

# Process data
processor = DataProcessor()
processed_requests = processor.process_and_validate_data(raw_requests)

# Update geodatabase
updater = DataUpdater()
updater.update_service_requests_table(processed_requests)
```

## Data Schema

The system creates a `SERVICE_REQUESTS` feature class with the following fields:

- **Geometry**: Point features with Web Mercator (EPSG:3857) X/Y coordinates
- **REQUESTID**: Unique request identifier
- **DESCRIPTION**: Service request description
- **STATUS**: Request status (New, Closed, etc.)
- **PROBADDRESS**: Problem address
- **PROBCITY**: City (defaults to St. Louis)
- **PROBZIP**: ZIP code
- **DATETIMEINIT**: Request initiation date/time
- **DATETIMECLOSED**: Request closure date/time
- **SUBMITTO**: Responsible agency
- **PROBLEMCODE**: Service code
- **SRX/SRY**: Web Mercator (EPSG:3857) X/Y coordinates (meters)

## Coordinate System

- **Input**: Web Mercator (EPSG:3857) X/Y meters from API (SRX/SRY, or fallback to LAT/LONG as X/Y in 3857)
- **Output**: Web Mercator (EPSG:3857) X/Y meters in geodatabase and ArcGIS Online
- **Validation**: St. Louis area bounds checking (in meters, 3857)
- **No conversion to or from latitude/longitude (4326) is performed.**

## Logging

The system provides comprehensive logging:

- **File**: `311_integration.log`
- **Level**: Configurable (INFO, DEBUG, WARNING, ERROR)
- **Format**: Timestamp, level, message

## Error Handling

The system includes robust error handling:

- **API Failures**: Retry logic with exponential backoff
- **Data Validation**: Coordinate and date validation
- **Geodatabase Errors**: Graceful handling of schema issues 