"""
Main execution module for St. Louis 311 Service Integration.
Provides command-line interface and main execution logic.
"""

import sys
from datetime import datetime, timedelta
from integration import StLouis311Integrator





def main():
    """
    Main execution function for the St. Louis 311 integration.
    """
    try:
        print("Starting St. Louis 311 Service Integration")
        
        # Initialize integrator
        integrator = StLouis311Integrator()
        
        # Check system status
        print("Checking system status...")
        status = integrator.get_integration_status()
        
        print("System status: Ready for integration")
        
        # Run integration
        print("Running integration...")
        result = integrator.run_integration()
        
        if result['status'] == 'success':
            print("Integration completed successfully!")
            print(f"Processed {result['total_requests_processed']} requests")
            print(f"Inserted {result['requests_inserted']} new records")
            print(f"Updated {result['requests_updated']} existing records")
            
            # Print validation summary
            validation = result.get('validation_summary', {})
            if validation:
                print(f"Validation: {validation['with_coordinates']}/{validation['total_processed']} requests have coordinates")
                print(f"Coordinate percentage: {validation['coordinate_percentage']:.1f}%")
            
            return 0
        else:
            print(f"Integration failed: {result.get('message', result.get('error', 'Unknown error'))}")
            return 1
            
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 