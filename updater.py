"""
Data updater module for St. Louis 311 Service Integration.
Handles geodatabase updates and data insertion.
"""

import arcpy
from datetime import datetime as dt
from config import SERVICE_REQUESTS_SCHEMA


class DataUpdater:
    """
    Professional data updater for St. Louis 311 service requests.
    Handles geodatabase updates and data insertion.
    """
    
    def __init__(self, gdb_manager):
        self.gdb_manager = gdb_manager
    
    def update_service_requests_table(self, processed_requests):
        """
        Update the service requests feature class with processed data.
        Uses upsert strategy: insert new, update existing, don't delete old.
        """
        if not processed_requests:
            print("No processed requests to update")
            return {'inserted': 0, 'updated': 0}
        
        try:
            # Ensure feature class exists with correct schema
            self._ensure_feature_class_exists()
            
            # Get feature class path
            fc_path = self.gdb_manager.get_feature_class_path('SERVICE_REQUESTS')
            
            # Get existing REQUESTID values to check for duplicates
            existing_request_ids = set()
            with arcpy.da.SearchCursor(fc_path, ['REQUESTID']) as cursor:
                for row in cursor:
                    if row[0] is not None:
                        existing_request_ids.add(row[0])
            
            print(f"Found {len(existing_request_ids)} existing records in feature class")
            
            # Prepare data for insertion
            insert_data = []
            update_data = []
            
            for request in processed_requests:
                request_id = request.get('REQUESTID')
                
                # Convert datetime objects to strings for ArcPy
                row_data = {}
                for field, value in request.items():
                    if isinstance(value, dt):
                        # Convert datetime to string format that ArcPy can handle
                        row_data[field] = value.strftime('%Y-%m-%d %H:%M:%S')
                    elif field in ['DATECANCELLED', 'DATEINVTDONE', 'DATETIMECLOSED', 'DATETIMEINIT', 'PRJCOMPLETEDATE']:
                        # Handle date fields - convert empty strings to None
                        if value == '' or value is None:
                            row_data[field] = None
                        else:
                            row_data[field] = value
                    else:
                        row_data[field] = value
                
                # Check if this request already exists
                if request_id in existing_request_ids:
                    update_data.append(row_data)
                else:
                    insert_data.append(row_data)
            
            print(f"Prepared {len(insert_data)} new records and {len(update_data)} existing records for update")
            
            # Insert new records
            inserted_count = 0
            with arcpy.da.InsertCursor(fc_path, ['SHAPE'] + [f for f in SERVICE_REQUESTS_SCHEMA.keys() if f != 'SHAPE']) as cursor:
                for row_data in insert_data:
                    try:
                        # Create point geometry from coordinates
                        x_coord = row_data.get('SRX')
                        y_coord = row_data.get('SRY')
                        
                        if x_coord is not None and y_coord is not None:
                            # Create point geometry in 3857 directly
                            point = arcpy.Point(x_coord, y_coord)
                            point_geometry_3857 = arcpy.PointGeometry(point, arcpy.SpatialReference(3857))
                            
                            # Create row tuple with geometry first, then other fields
                            row_tuple = [point_geometry_3857] + [row_data.get(field, None) for field in SERVICE_REQUESTS_SCHEMA.keys() if field != 'SHAPE']
                            cursor.insertRow(row_tuple)
                            inserted_count += 1
                        else:
                            print(f"Skipping record with missing coordinates: {row_data.get('REQUESTID')}")
                    except Exception as e:
                        print(f"Failed to insert row: {e}")
                        continue
            
            # Update existing records
            updated_count = 0
            if update_data:
                # For updates, we need to use UpdateCursor with a WHERE clause
                # Since ArcPy doesn't support complex WHERE clauses easily, we'll use a different approach
                # We'll delete the old records and insert the updated ones
                with arcpy.da.UpdateCursor(fc_path, ['REQUESTID'] + list(SERVICE_REQUESTS_SCHEMA.keys())) as cursor:
                    for row in cursor:
                        request_id = row[0]
                        if request_id in [r.get('REQUESTID') for r in update_data]:
                            # Find the updated data for this request
                            updated_row = next((r for r in update_data if r.get('REQUESTID') == request_id), None)
                            if updated_row:
                                # Update the row with new data
                                updated_tuple = tuple(updated_row.get(field, None) for field in SERVICE_REQUESTS_SCHEMA.keys())
                                cursor.updateRow([request_id] + list(updated_tuple))
                                updated_count += 1
            
            print(f"Successfully inserted {inserted_count} new records and updated {updated_count} existing records")
            return {'inserted': inserted_count, 'updated': updated_count}
            
        except Exception as e:
            print(f"Error updating service requests table: {e}")
            raise
    
    def _ensure_feature_class_exists(self):
        """
        Ensure the service requests feature class exists with correct schema.
        """
        try:
            fc_path = self.gdb_manager.get_feature_class_path('SERVICE_REQUESTS')
            
            # Check if feature class exists
            if arcpy.Exists(fc_path):
                print("Service requests feature class already exists")
                return
            
            # Create feature class with schema
            print("Creating service requests feature class...")
            
            # Create the feature class
            arcpy.CreateFeatureclass_management(
                out_path=self.gdb_manager.gdb_path,
                out_name='SERVICE_REQUESTS',
                geometry_type='POINT',
                spatial_reference=arcpy.SpatialReference(3857)  # Web Mercator
            )
            
            # Add fields according to schema
            for field_name, field_type in SERVICE_REQUESTS_SCHEMA.items():
                if field_name not in ['SHAPE', 'OBJECTID']:  # Skip geometry and OID fields
                    try:
                        if field_type == 'TEXT':
                            arcpy.AddField_management(fc_path, field_name, 'TEXT', field_length=255)
                        elif field_type == 'LONG':
                            arcpy.AddField_management(fc_path, field_name, 'LONG')
                        elif field_type == 'DOUBLE':
                            arcpy.AddField_management(fc_path, field_name, 'DOUBLE')
                        elif field_type == 'DATE':
                            arcpy.AddField_management(fc_path, field_name, 'DATE')
                    except Exception as e:
                        print(f"Field {field_name} may already exist: {e}")
            
            print("Service requests feature class created successfully")
            
        except Exception as e:
            print(f"Error ensuring feature class exists: {e}")
            raise 