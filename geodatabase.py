"""
Geodatabase management module for St. Louis 311 Service Integration.
Handles geodatabase creation, schema setup, and infrastructure management.
"""

import arcpy
import os
from config import SERVICE_REQUESTS_SCHEMA, COORDINATE_SYSTEM


class GeodatabaseManager:
    """
    Professional geodatabase management class for St. Louis 311 service requests.
    Handles geodatabase creation, feature class setup, and schema management.
    """
    
    def __init__(self, geodatabase_path=None, coordinate_system=COORDINATE_SYSTEM):
        from config import GEODATABASE_PATH
        self.gdb_path = geodatabase_path or GEODATABASE_PATH
        self.coordinate_system = coordinate_system
    
    def setup_geodatabase(self):
        """
        Create geodatabase and feature classes with professional schema.
        Real-world GIS developers must handle data modeling properly.
        """
        try:
            # Create geodatabase if it doesn't exist
            if not arcpy.Exists(self.gdb_path):
                gdb_folder = os.path.dirname(self.gdb_path)
                gdb_name = os.path.basename(self.gdb_path)
                arcpy.CreateFileGDB_management(gdb_folder, gdb_name)
                print(f"Created geodatabase: {self.gdb_path}")
            
            # Create SERVICE_REQUESTS feature class
            fc_name = 'SERVICE_REQUESTS'
            fc_path = os.path.join(self.gdb_path, fc_name)
            
            # Check if feature class exists and has correct coordinate system
            if arcpy.Exists(fc_path):
                # Get the current spatial reference
                desc = arcpy.Describe(fc_path)
                current_sr = desc.spatialReference
                print(f"Current feature class coordinate system: {current_sr.name} (EPSG:{current_sr.factoryCode})")
                
                # If coordinate system doesn't match, delete and recreate
                if current_sr.factoryCode != 4326:  # WGS84
                    print("Coordinate system mismatch. Deleting and recreating feature class...")
                    arcpy.Delete_management(fc_path)
                    print(f"Deleted existing feature class: {fc_name}")
                else:
                    print(f"Feature class already exists with correct coordinate system: {fc_name}")
                    return
            
            # Create feature class with WGS84 coordinate system
            arcpy.CreateFeatureclass_management(
                self.gdb_path, 
                fc_name,
                'POINT',
                spatial_reference=arcpy.SpatialReference(4326)  # WGS84 Geographic
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
            
            print(f"Created feature class with WGS84 coordinate system: {fc_name}")
                    
        except Exception as e:
            print(f"Error setting up geodatabase: {str(e)}")
            raise
    
    def get_feature_class_path(self, feature_class_name):
        """
        Get the full path to a feature class or table.
        """
        return os.path.join(self.gdb_path, feature_class_name)
    
    def feature_class_exists(self, feature_class_name):
        """
        Check if a feature class or table exists.
        """
        fc_path = self.get_feature_class_path(feature_class_name)
        return arcpy.Exists(fc_path)
    
    def get_field_names(self, feature_class_name):
        """
        Get field names for a feature class or table.
        """
        fc_path = self.get_feature_class_path(feature_class_name)
        if not arcpy.Exists(fc_path):
            raise ValueError(f"Feature class {feature_class_name} does not exist")
        
        fields = arcpy.ListFields(fc_path)
        return [field.name for field in fields]
    