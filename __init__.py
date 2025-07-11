"""
St. Louis 311 Service Integration Package.

A professional GIS integration system for St. Louis 311 service requests.
Provides modular components for API integration, data processing, and analysis.

Modules:
    - config: Configuration settings and constants
    - geodatabase: Geodatabase setup and schema management
    - api_client: API interaction and data fetching
    - processor: Data cleaning and validation
    - updater: Database insert and update operations
    - integration: Main integration orchestrator
    - main: Entry point and usage examples
"""

from .integration import StLouis311ServiceIntegrator
from .config import *
from .geodatabase import GeodatabaseManager
from .api_client import StLouisAPIClient
from .processor import DataProcessor
from .updater import DatabaseUpdater

__version__ = "1.0.0"
__author__ = "Maxx Millstein"
__description__ = "St. Louis 311 Service Integration System"

# Convenient imports for users
__all__ = [
    'StLouis311ServiceIntegrator',
    'GeodatabaseManager',
    'StLouisAPIClient',
    'DataProcessor',
    'DatabaseUpdater'
] 