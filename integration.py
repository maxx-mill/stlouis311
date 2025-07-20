import os
from datetime import datetime as dt
from api_client import APIClient
from processor import DataProcessor
from updater import DataUpdater
from geodatabase import GeodatabaseManager
from arc_gis_online_publisher import ArcGISOnlinePublisher
from config import START_DATE, END_DATE, DEFAULT_STATUS
import arcpy
import time 

class StLouis311Integrator:
    """
    Professional integrator for St. Louis 311 service requests with ArcGIS Online publishing.
    Orchestrates the complete data integration workflow including online publishing.
    """
    
    def __init__(self, gdb_path=None, arcgis_credentials=None):
        """
        Initialize the integrator with optional ArcGIS Online credentials.
        
        Args:
            gdb_path: Path to the geodatabase
            arcgis_credentials: Dict with 'username', 'password', and optional 'portal_url'
        """
        self.gdb_manager = GeodatabaseManager(gdb_path)
        self.api_client = APIClient()
        self.processor = DataProcessor()
        self.updater = DataUpdater(self.gdb_manager)
        
        # Initialize ArcGIS Online publisher if credentials provided
        # Use 'arcgis_credentials' to pass parameters to the publisher
        self.publisher = ArcGISOnlinePublisher(
            portal_url=arcgis_credentials.get('portal_url') # Corrected variable name here
        )
    
    def run_integration(self, start_date=None, end_date=None, status=None, publish_online=True, service_name='StLouis311_ServiceRequests', update_method='replace'):
        """
        Run the complete integration workflow and optionally publish to ArcGIS Online.
        Args:
            start_date: Start date for data fetching
            end_date: End date for data fetching
            status: Status filter for requests
            publish_online: Whether to publish to ArcGIS Online
            service_name: Name of the ArcGIS Online service
            update_method: Method for updating the service ('replace' or other)
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

            print("Releasing geodatabase locks and compacting...")
            arcpy.Compact_management(self.gdb_manager.gdb_path)  # Ensure locks are released
            print("Geodatabase locks released and compacted.")

            # Step 4: Optionally publish to ArcGIS Online
            online_result = None
            if publish_online and self.publisher: # Corrected attribute name here
                print("Step 4: Publishing to ArcGIS Online...")
                online_result = self._publish_to_arcgis_online_custom(service_name, update_method)
            elif publish_online:
                print("Warning: ArcGIS Online publisher not available")

            # Step 5: Generate summary
            print("Step 5: Generating integration summary...")
            summary = self._generate_summary(processed_requests, update_result, online_result)

            print("Integration completed successfully")
            return summary

        except Exception as e:
            print(f"Integration failed: {e}")
            return {'status': 'error', 'error': str(e)}

    def _publish_to_arcgis_online_custom(self, service_name, update_method):
        """
        Publish or update the geodatabase to ArcGIS Online using custom service name and method.
        """
        try:
            if not self.publisher: # Corrected attribute name here
                return {'status': 'error', 'message': 'ArcGIS Online publisher not available'}

            folder = 'StLouis311'
            service_exists = self.publisher.service_exists(service_name)

            if not service_exists:
                print(f"Publishing new service: {service_name}")
                feature_service = self.publisher.publish_feature_service(
                    gdb_path=self.gdb_manager.gdb_path,
                    service_name=service_name,
                    folder=folder,
                    overwrite=False
                )
                if feature_service:
                    return {
                        'status': 'published',
                        'service_name': service_name,
                        'service_url': feature_service.url,
                        'action': 'new_service'
                    }
                else:
                    return {'status': 'error', 'message': 'Failed to publish new service'}
            else:
                print(f"Updating existing service: {service_name}")
                update_result = self.publisher.update_feature_service(
                    service_name=service_name,
                    gdb_path=self.gdb_manager.gdb_path,
                    update_method=update_method
                )
                if update_result and update_result.get('status') == 'success':
                    return {
                        'status': 'updated',
                        'service_name': service_name,
                        'service_url': update_result.get('service_url'),
                        'action': 'service_update',
                        'update_method': update_method,
                        'features_processed': update_result.get('features_processed', 0)
                    }
                else:
                    return {'status': 'error', 'message': 'Failed to update service'}
        except Exception as e:
            print(f"Error publishing to ArcGIS Online: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _generate_summary(self, processed_requests, update_result, online_result=None):
        """
        Generate a comprehensive integration summary.
        """
        validation_summary = self.processor.get_validation_summary(processed_requests)
        
        summary = {
            'status': 'success',
            'timestamp': dt.now().isoformat(),
            'total_requests_processed': len(processed_requests),
            'requests_inserted': update_result.get('inserted', 0),
            'requests_updated': update_result.get('updated', 0),
            'validation_summary': validation_summary,
            'geodatabase_path': self.gdb_manager.gdb_path
        }
        
        # Add online publishing results if available
        if online_result:
            summary['online_publishing'] = online_result
        
        return summary