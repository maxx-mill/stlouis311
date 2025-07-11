"""
Integration module for St. Louis 311 Service Integration.
Orchestrates the complete data integration workflow.
"""

from datetime import datetime
from api_client import APIClient
from processor import DataProcessor
from updater import DataUpdater
from geodatabase import GeodatabaseManager
from config import START_DATE, END_DATE, DEFAULT_STATUS


class StLouis311Integrator:
    """
    Professional integrator for St. Louis 311 service requests.
    Orchestrates the complete data integration workflow.
    """
    
    def __init__(self, gdb_path=None):
        self.gdb_manager = GeodatabaseManager(gdb_path)
        self.api_client = APIClient()
        self.processor = DataProcessor()
        self.updater = DataUpdater(self.gdb_manager)
    
    def run_integration(self, start_date=None, end_date=None, status=None):
        """
        Run the complete integration workflow.
        """
        try:
            print("Starting St. Louis 311 integration...")
            
            # Step 0: Setup geodatabase if it doesn't exist
            print("Step 0: Setting up geodatabase...")
            self.gdb_manager.setup_geodatabase()
            
            # Step 1: Fetch service requests from API
            print("Step 1: Fetching service requests from API...")
            raw_requests = self.api_client.fetch_service_requests(
                start_date=start_date or START_DATE,
                end_date=end_date or END_DATE,
                status=status or DEFAULT_STATUS
            )
            
            if not raw_requests:
                print("No service requests found")
                return {'status': 'no_data', 'message': 'No service requests found'}
            
            # Step 2: Process and validate data
            print("Step 2: Processing and validating data...")
            processed_requests = self.processor.process_and_validate_data(raw_requests)
            
            if not processed_requests:
                print("No valid service requests after processing")
                return {'status': 'no_valid_data', 'message': 'No valid service requests after processing'}
            
            # Step 3: Update geodatabase
            print("Step 3: Updating geodatabase...")
            update_result = self.updater.update_service_requests_table(processed_requests)
            
            # Step 4: Generate summary
            print("Step 4: Generating integration summary...")
            summary = self._generate_summary(processed_requests, update_result)
            
            print("Integration completed successfully")
            return summary
            
        except Exception as e:
            print(f"Integration failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _generate_summary(self, processed_requests, update_result):
        """
        Generate a comprehensive integration summary.
        """
        validation_summary = self.processor.get_validation_summary(processed_requests)
        
        return {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'total_requests_processed': len(processed_requests),
            'requests_inserted': update_result.get('inserted', 0),
            'requests_updated': update_result.get('updated', 0),
            'validation_summary': validation_summary,
            'geodatabase_path': self.gdb_manager.gdb_path
        }
    
    def get_integration_status(self):
        """
        Get the current status of the integration system.
        """
        try:
            return {
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            } 