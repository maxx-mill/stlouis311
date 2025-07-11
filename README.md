# St. Louis 311 Service Integration

A professional, modular Python integration system for St. Louis 311 service requests using ArcPy. This system fetches service requests from the St. Louis Open311 API, processes and validates the data, and stores it in a geodatabase.

## Features

- **Modular Architecture**: Clean separation of concerns with dedicated modules for API, processing, and geodatabase
- **Professional Data Processing**: Robust data validation, coordinate transformation, and error handling
- **ArcGIS Integration**: Native geodatabase support with proper coordinate systems
- **Comprehensive Logging**: Professional logging with configurable levels
- **Coordinate Transformation**: Automatic conversion from Web Mercator to WGS84 coordinates

## Project Structure

```
stlouis311/
├── main.py              # Main execution script
├── integration.py       # Integration orchestrator
├── api_client.py        # API client for St. Louis Open311
├── processor.py         # Data processing and validation
├── updater.py          # Geodatabase updates
├── geodatabase.py      # Geodatabase management

├── config.py           # Configuration settings
├── README.md           # This file
└── StLouis311.gdb/     # ArcGIS geodatabase
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

## Configuration

Edit `config.py` to configure:

- **API Settings**: API key, base URL, request parameters
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
3. Transform coordinates from Web Mercator to WGS84
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

- **Geometry**: Point features with WGS84 coordinates
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
- **SRX/SRY**: WGS84 coordinates (Longitude/Latitude)

## Coordinate System

- **Input**: Web Mercator (EPSG:3857) from API
- **Output**: WGS84 Geographic (EPSG:4326) in geodatabase
- **Validation**: St. Louis area bounds checking

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
- **Missing Data**: Intelligent defaults and field mapping

## Development

### Adding New Fields

1. Update `SERVICE_REQUESTS_SCHEMA` in `config.py`
2. Add field mapping in `processor.py`
3. Update geodatabase schema if needed

### Extending Functionality

- **New Data Sources**: Extend `APIClient` class
- **Additional Processing**: Add methods to `DataProcessor`


## Troubleshooting

### Common Issues

1. **ArcPy Import Error**: Ensure running in ArcGIS Pro Python environment
2. **Coordinate Issues**: Check coordinate system settings in config
3. **API Errors**: Verify API key and network connectivity
4. **Geodatabase Errors**: Check file permissions and paths

### Debug Mode

Enable debug logging in `config.py`:

```python
LOG_LEVEL = "DEBUG"
```

## License

This project is for professional GIS applications and follows best practices for data integration and geospatial processing. 