"""
ArcGIS Online publisher module for St. Louis 311 Service Integration.
Handles publishing and updating feature services on ArcGIS Online.
"""
import traceback
import os
import json
import zipfile
import tempfile
import arcpy # Still needed for arcpy.Exists and arcpy.da.SearchCursor
from datetime import datetime as dt
from arcgis.gis import GIS
from arcgis.features import FeatureLayerCollection, FeatureSet
from arcgis.geometry import Point, Geometry


class ArcGISOnlinePublisher:
    def __init__(self, portal_url='https://www.arcgis.com'):
        """
        Initialize the ArcGIS Online publisher using ArcGIS Pro's active portal connection.

        Args:
            portal_url (str, optional): ArcGIS Online organization URL. 
                                        Defaults to 'https://www.arcgis.com'.
                                        If an active portal connection exists in ArcGIS Pro,
                                        this URL will be used to connect to it.
        """
        try:
            # Use "pro" to connect via ArcGIS Pro's active portal
            # The portal_url parameter for GIS("pro", portal_url) is used to specify
            # which portal connection to use if multiple are configured in ArcGIS Pro.
            self.gis = GIS("pro")
            self.username = self.gis.users.me.username
            self.portal_url = portal_url
            print(f"Successfully connected to ArcGIS Online as {self.username} via ArcGIS Pro.")
        except Exception as e:
            print(f"Failed to connect to ArcGIS Online via ArcGIS Pro: {e}")
            # Raising the exception ensures that the program stops if authentication fails
            raise
    
    def _create_service_zip(self, gdb_path, service_name):
        """
        Create a zip archive of the file geodatabase for upload.
        Explicitly excludes common lock and temporary files.
        """
        zip_path = os.path.join(tempfile.gettempdir(), f"{service_name}.zip")
        
        # Ensure the temp directory exists
        os.makedirs(os.path.dirname(zip_path), exist_ok=True)

        # Define files/extensions to exclude (case-insensitive check by converting file.lower())
        EXCLUDE_EXTENSIONS = ('.lock', '.sr.lock', '.atx', '.freelist')
        # Specific common lock/temp file names that might not end with just the extension
        EXCLUDE_FILES = ('_gdb.atx', '_gdb.atx_lock', '_gdb.freelist', '_gdb.freelist_lock') 

        print(f"Attempting to create GDB zip file from: {gdb_path}")

        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(gdb_path):
                    for file in files:
                        file_lower = file.lower() # Convert to lowercase once for case-insensitive comparison
                        
                        # Check if the file should be excluded
                        should_exclude = False
                        if file_lower in EXCLUDE_FILES: # Check specific file names
                            should_exclude = True
                        else: # Check file extensions
                            for ext in EXCLUDE_EXTENSIONS:
                                if file_lower.endswith(ext):
                                    should_exclude = True
                                    break # No need to check other extensions

                        if should_exclude:
                            print(f"Skipping internal GDB file: {file}")
                            continue # Skip this file and go to the next one

                        file_path = os.path.join(root, file)
                        # For consistency, make sure the root name is not included in the archive path
                        # os.path.relpath(file_path, gdb_path) gives path relative to gdb_path.
                        # os.path.basename(gdb_path) ensures the GDB folder itself is the root in the zip.
                        arcname = os.path.join(os.path.basename(gdb_path), os.path.relpath(file_path, gdb_path))
                        
                        # print(f"Adding to zip: {file_path} as {arcname}") # Uncomment for verbose debugging
                        
                        zipf.write(file_path, arcname)
            print(f"Successfully created GDB zip file: {zip_path}")
            return zip_path
            
        except PermissionError as pe:
            print(f"Error during zip file creation (PermissionError): {pe}")
            print(f"The file causing the error was likely: {file_path}")
            raise # Re-raise to show in main error handling
        except Exception as e:
            print(f"An unexpected error occurred during zip file creation: {e}")
            raise
            
        except PermissionError as pe:
            print(f"Error during zip file creation (PermissionError): {pe}")
            print(f"The file causing the error was likely: {file_path}")
            raise # Re-raise to show in main error handling
        except Exception as e:
            print(f"An unexpected error occurred during zip file creation: {e}")
            raise
    
    def publish_feature_service(self, gdb_path, service_name, folder=None, overwrite=False):
        """
        Publish geodatabase as a hosted feature service.
        
        Args:
            gdb_path: Path to the geodatabase
            service_name: Name for the feature service
            folder: Optional folder to organize the service
            overwrite: Whether to overwrite existing service
        """
        try:
            # Check if service already exists
            if self.service_exists(service_name) and not overwrite:
                print(f"Service {service_name} already exists. Use overwrite=True to replace.")
                return None
            
            # Define service properties
            service_properties = {
                'title': service_name,
                'description': 'St. Louis 311 Service Requests - Auto-updated from local geodatabase',
                'tags': ['311', 'St. Louis', 'service requests', 'government', 'open data'],
                'snippet': 'Real-time 311 service requests for the City of St. Louis',
                'accessInformation': 'City of St. Louis Open Data Portal',
                'licenseInfo': 'Public Domain',
                'type': 'File Geodatabase'
            }
            
            print(f"Publishing {gdb_path} as {service_name}...")
            
            # Create the zip file of the geodatabase
            zip_path = self._create_service_zip(gdb_path, service_name)
            
            # Upload zipped geodatabase
            print("Uploading zipped geodatabase...")
            
            # Construct arguments for gis.content.add dynamically
            add_kwargs = {
                'item_properties': service_properties,
                'data': zip_path
            }
            
            # Only add the 'folder' parameter if it's provided (not None)
            if isinstance(folder, str) and folder.strip():
                folder_names = [f['title'] for f in self.gis.users.me.folders]
                if folder not in folder_names:
                    self.gis.content.folders.create(folder)

                item = self.gis.content.add(
                    item_properties=service_properties,
                    data=zip_path,
                    folder=folder
                )
            else:
                item = self.gis.content.add(
                    item_properties=service_properties,
                    data=zip_path
                )

            
            # Publish as feature service
            print("Publishing feature service...")
            feature_service = item.publish(
                publish_parameters={
                    'name': service_name,
                    'hasStaticData': False,
                    'maxRecordCount': 10000,
                    'allowGeometryUpdates': True,
                    'capabilities': 'Query,Create,Update,Delete,Uploads,Editing',
                    'units': 'esriMeters',
                    'xssPreventionEnabled': True,
                    'spatialReference': {'wkid': 3857} # Web Mercator 
                }
            )
            
            # Clean up temporary files
            if os.path.exists(zip_path):
                os.remove(zip_path)
            
            print(f"Successfully published: {feature_service.url}")
            
            # Set sharing permissions
            self._configure_service_sharing(feature_service)
            
            return feature_service
            
        except Exception as e:
            print(f"Error publishing service: {e}")
            raise
    
    def update_feature_service(self, service_name, gdb_path, update_method='replace'):
        """
        Update existing feature service with new data.
        
        Args:
            service_name: Name of the existing service
            gdb_path: Path to the geodatabase with updated data
            update_method: 'replace' (truncate and reload) or 'append' (add new records)
        """
        try:
            # Find the existing service
            service_item = self.find_service(service_name)
            if not service_item:
                print(f"Service {service_name} not found. Publishing new service...")
                return self.publish_feature_service(gdb_path, service_name)
            
            print(f"Updating existing service: {service_name}")
            
            # Get the feature service
            feature_service = FeatureLayerCollection.fromitem(service_item)
            feature_layer = feature_service.layers[0]
            
            # Get data from local geodatabase
            fc_path = os.path.join(gdb_path, 'SERVICE_REQUESTS')
            if not arcpy.Exists(fc_path):
                raise ValueError(f"Feature class SERVICE_REQUESTS not found in {gdb_path}")
            
            # Convert geodatabase data to feature set
            feature_set = self._gdb_to_feature_set(fc_path)
            
            if update_method == 'replace':
                # Truncate existing data
                print("Truncating existing data...")
                delete_result = feature_layer.delete_features(where="1=1")
                # print(f"Deleted {delete_result.get('deleteResults', [])} features") # This can be very verbose, simplified below
                deleted_count = sum([r.get('objectId') is not None for r in delete_result.get('deleteResults', [])])
                print(f"Attempted to delete {deleted_count} features (or all if successful).")
                
                # Add new data
                print(f"Adding {len(feature_set)} new features...")
                add_result = feature_layer.edit_features(adds=feature_set)
                
                if add_result and 'addResults' in add_result:
                    success_count = len([r for r in add_result.get('addResults', []) if r.get('success')])
                    print(f"Successfully added {success_count} features")
                else:
                    print("Error: No result returned from edit_features.")
                    success_count = 0
                
            elif update_method == 'append':
                # Add new data without truncating
                print(f"Appending {len(feature_set)} features...")
                add_result = feature_layer.edit_features(adds=feature_set)
                
                if add_result and 'addResults' in add_result:
                    success_count = len([r for r in add_result.get('addResults', []) if r.get('success')])
                    print(f"Successfully added {success_count} features")
                else:
                    print("Error: No result returned from edit_features.")
                    success_count = 0
                  
            # Update service metadata (optional, but good for tracking)
            service_item.update(
                item_properties={
                    'snippet': f'Updated {dt.now().strftime("%Y-%m-%d %H:%M:%S")} - {success_count} records via {update_method}'
                }
            )
            
            return {
                'status': 'success',
                'features_processed': success_count,
                'update_method': update_method,
                'service_url': feature_service.url
            }
            
        except Exception as e:
            print(f"\n--- ERROR DURING UPDATE ---")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {e}")
            print("\nFull traceback:")
            traceback.print_exc()
            print(f"---------------------------")
            raise
    
    def incremental_update(self, service_name, gdb_path, id_field='REQUESTID'):
        """
        Perform incremental update by comparing local and online data.
        
        Args:
            service_name: Name of the service to update
            gdb_path: Path to local geodatabase
            id_field: Field to use for comparing records
        """
        try:
            service_item = self.find_service(service_name)
            if not service_item:
                return self.publish_feature_service(gdb_path, service_name)
            
            feature_service = FeatureLayerCollection.fromitem(service_item)
            feature_layer = feature_service.layers[0]
            
            # Get existing IDs from online service
            print("Fetching existing record IDs from ArcGIS Online...")
            existing_query = feature_layer.query(
                where="1=1",
                out_fields=id_field,
                return_geometry=False
            )
            
            existing_ids = set()
            for feature in existing_query.features:
                if feature.attributes.get(id_field):
                    existing_ids.add(feature.attributes[id_field])
            
            print(f"Found {len(existing_ids)} existing records online")
            
            # Get local data
            fc_path = os.path.join(gdb_path, 'SERVICE_REQUESTS')
            local_features = self._gdb_to_feature_set(fc_path)
            
            # Identify new records
            new_features = []
            for feature in local_features:
                if feature['attributes'].get(id_field) not in existing_ids:
                    new_features.append(feature)
            
            print(f"Found {len(new_features)} new records to add")
            
            # Add new records
            if new_features:
                add_result = feature_layer.edit_features(adds=new_features)
                success_count = len([r for r in add_result.get('addResults', []) if r.get('success')])
                print(f"Successfully added {success_count} new records")
            else:
                print("No new records to add.")
            
            return {
                'status': 'success',
                'new_records': len(new_features),
                'existing_records': len(existing_ids),
                'total_local': len(local_features)
            }
            
        except Exception as e:
            print(f"\n--- ERROR IN INCREMENTAL UPDATE ---")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {e}")
            print("\nFull traceback:")
            traceback.print_exc()
            print(f"---------------------------------")
            raise
    
    def service_exists(self, service_name):
        """Check if a service with the given name exists."""
        try:
            search_results = self.gis.content.search(
                query=f"title:\"{service_name}\" owner:\"{self.username}\"", # Use quotes for robust search
                item_type="Feature Service"
            )
            return len(search_results) > 0
        except Exception as e:
            print(f"Error checking service existence: {e}")
            return False
    
    def find_service(self, service_name):
        """Find a service by name."""
        try:
            search_results = self.gis.content.search(
                query=f"title:\"{service_name}\" owner:\"{self.username}\"", # Use quotes for robust search
                item_type="Feature Service"
            )
            return search_results[0] if search_results else None
        except Exception as e:
            print(f"Error finding service: {e}")
            return None
    
    def get_service_info(self, service_name):
        """Get information about a service."""
        try:
            service_item = self.find_service(service_name)
            if not service_item:
                return None
            
            feature_service = FeatureLayerCollection.fromitem(service_item)
            feature_layer = feature_service.layers[0]
            
            # Get feature count
            count_result = feature_layer.query(
                where="1=1",
                return_count_only=True
            )
            
            return {
                'service_name': service_name,
                'service_id': service_item.id,
                'url': feature_service.url,
                'feature_count': count_result,
                'last_modified': service_item.modified,
                'owner': service_item.owner,
                'sharing': service_item.shared_with
            }
        except Exception as e:
            print(f"Error getting service info: {e}")
            return None
            
    
    def _gdb_to_feature_set(self, fc_path):
    #Convert geodatabase feature class to feature set for upload
        try:
            features = []
            
            # Get field information
            fields = arcpy.ListFields(fc_path)
            field_names = [f.name for f in fields if f.type not in ['OID', 'Geometry'] and f.name != 'Shape']
            
            # Read features using SRX and SRY coordinate fields directly
            cursor_fields = field_names + ['SRX', 'SRY'] if 'SRX' in [f.name for f in fields] and 'SRY' in [f.name for f in fields] else field_names + ['SHAPE@']
            
            with arcpy.da.SearchCursor(fc_path, cursor_fields) as cursor:
                for row in cursor:
                    # Create attributes dictionary
                    attributes = {}
                    for i, field_name in enumerate(field_names):
                        value = row[i]
                        
                        # Handle date fields
                        if isinstance(value, dt):
                            attributes[field_name] = int(value.timestamp() * 1000)   # Convert to milliseconds
                        elif value is None:
                            attributes[field_name] = None
                        else:
                            attributes[field_name] = value
                    
                    # Handle geometry - always treat SRX/SRY as 3857 (Web Mercator)
                    geometry = None
                    if len(cursor_fields) > len(field_names):
                        if 'SRX' in cursor_fields and 'SRY' in cursor_fields:
                            srx_idx = cursor_fields.index('SRX')
                            sry_idx = cursor_fields.index('SRY')
                            x_coord = row[srx_idx]
                            y_coord = row[sry_idx]
                            if x_coord is not None and y_coord is not None:
                                # Create point geometry in 3857 directly
                                point_3857 = arcpy.PointGeometry(
                                    arcpy.Point(float(x_coord), float(y_coord)), 
                                    arcpy.SpatialReference(3857)  # Web Mercator
                                )
                                if point_3857 and point_3857.firstPoint:
                                    geometry = {
                                        'x': point_3857.firstPoint.X,
                                        'y': point_3857.firstPoint.Y,
                                        'spatialReference': {'wkid': 3857}
                                    }
                                else:
                                    print(f"Warning: Invalid geometry for attributes {attributes}. Skipping feature.")
                                    continue
                        else:
                            shape = row[-1]
                            if shape:
                                web_mercator_shape = shape.projectAs(arcpy.SpatialReference(3857))
                                if web_mercator_shape and web_mercator_shape.centroid:
                                    geometry = {
                                        'x': web_mercator_shape.centroid.X,
                                        'y': web_mercator_shape.centroid.Y,
                                        'spatialReference': {'wkid': 3857}
                                    }
                                else:
                                    print(f"Warning: Invalid shape geometry for attributes {attributes}. Skipping feature.")
                                    continue
                    if geometry:
                        feature = {
                            'attributes': attributes,
                            'geometry': geometry
                        }
                        features.append(feature)
            
            print(f"Converted {len(features)} features from geodatabase to Web Mercator (3857)")
            return features
            
        except Exception as e:
            print(f"Error converting geodatabase to feature set: {e}")
            raise

    def _configure_service_sharing(self, feature_service):
        """Configure sharing settings for the service."""
        try:
            # Share with everyone (public)
            feature_service.share(everyone=True)
            print("Service shared publicly")
        except Exception as e:
            print(f"Error configuring service sharing: {e}")