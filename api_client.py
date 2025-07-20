"""
API client module for St. Louis 311 Service Integration.
Handles communication with the St. Louis Open311 API.
"""

import requests
import time
from datetime import datetime as dt, timedelta
from config import (
    API_BASE_URL, API_KEY, RATE_LIMIT_DELAY, MAX_PAGES,
    START_DATE, END_DATE, DEFAULT_STATUS
)


class APIClient:
    """
    Professional API client for St. Louis 311 service requests.
    Handles authentication, rate limiting, and data fetching.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'StLouis311-Integration/1.0',
            'Accept': 'application/json'
        })
    
    def fetch_service_requests(self, start_date=None, end_date=None, status=None):
        """
        Fetch service requests from the St. Louis Open311 API.
        Uses the batch endpoint with pagination support.
        """
        if not start_date:
            start_date = START_DATE
        if not end_date:
            end_date = END_DATE
        if not status:
            status = DEFAULT_STATUS
            
        all_requests = []
        page = 1
        
        while page <= MAX_PAGES:
            try:
                # Build query parameters
                params = {
                    'api_key': API_KEY,  # Add API key for authentication
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'page_size': 1000  # Maximum page size
                }
                
                # Add status parameter if specified
                if status:
                    params['status'] = status
                
                # Make API request
                url = f"{API_BASE_URL}/requests.json"
                print(f"Fetching page {page} from {url}")
                
                response = self.session.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Debug: Print response structure
                print(f"API response type: {type(data)}")
                if isinstance(data, dict):
                    print(f"API response keys: {list(data.keys())}")
                
                # API returns dictionary with service_requests key
                    requests_batch = data.get('service_requests', [])
                elif isinstance(data, list):
                    requests_batch = data
                else:
                    print(f"Unexpected API response format: {data}")
                    break
                
                if not requests_batch:
                    print(f"No more requests found on page {page}")
                    break
                
                all_requests.extend(requests_batch)
                print(f"Fetched {len(requests_batch)} requests from page {page}")
                
                # Check if we've reached the end
                if len(requests_batch) < 1000:
                    print(f"Reached end of data on page {page}")
                    break
                
                page += 1
                time.sleep(RATE_LIMIT_DELAY)  # Rate limiting
                
            except requests.exceptions.RequestException as e:
                print(f"API request failed on page {page}: {e}")
                break
            except Exception as e:
                print(f"Unexpected error on page {page}: {e}")
                break
        
        print(f"Total requests fetched: {len(all_requests)}")
        return all_requests 