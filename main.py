"""
Enhanced main execution module for St. Louis 311 Service Integration with ArcGIS Online publishing using OAuth 2.0.
Provides command-line interface and main execution logic with online publishing capabilities.
"""

import sys
import argparse
from datetime import datetime as dt, timedelta
from config import ARCGIS_OAUTH_CONFIG
from integration import StLouis311Integrator


def get_arcgis_oauth_config():
    """
    Get ArcGIS Online configuration.
    Returns a dictionary with portal_url, as GIS("pro") handles direct authentication.
    """
    # Only get portal_url from config, other OAuth details are not used for GIS("pro")
    portal_url = ARCGIS_OAUTH_CONFIG.get('portal_url', 'https://www.arcgis.com')
    
    # No "if not client_id:" check needed as we are not relying on client_id for this auth method.
    return {
        'portal_url': portal_url
    }


def parse_arguments():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(
        description='St. Louis 311 Service Integration with ArcGIS Online Publishing (OAuth)'
    )
    parser.add_argument('--days-back', type=int, default=1,
                       help='Number of days back to fetch data (default: 1)')
    parser.add_argument('--status', type=str, default='open',
                       help='Status filter for requests (default: open)')
    return parser.parse_args()


def main():
    """
    Main execution function for the St. Louis 311 integration with ArcGIS Online publishing.
    """
    try:
        # Parse command line arguments
        args = parse_arguments()

        print("=" * 60)
        print("St. Louis 311 Service Integration with ArcGIS Online Publishing (OAuth)")
        print("=" * 60)

        # Load OAuth credentials
        credentials = get_arcgis_oauth_config()
        if not credentials:
            print("Error: ArcGIS Online OAuth configuration not available. Exiting.")
            return 1

        # Initialize integrator
        integrator = StLouis311Integrator(arcgis_credentials=credentials)

        # Calculate date range
        end_date = dt.now()
        start_date = end_date - timedelta(days=args.days_back)

        print(f"Fetching data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print(f"Status filter: {args.status}")
        print(f"Will publish to ArcGIS Online as: StLouis311_ServiceRequests")
        print(f"Update method: replace")

        # Run integration
        print("\nRunning integration...")
        result = integrator.run_integration(
            start_date=start_date,
            end_date=end_date,
            status=args.status,
            publish_online=True,
            service_name='StLouis311_ServiceRequests',
            update_method='replace'
        )

        if result['status'] == 'success':
            print("\nIntegration completed successfully!")
            print(f"  Processed {result['total_requests_processed']} requests")
            print(f"  Inserted {result['requests_inserted']} new records")
            print(f"  Updated {result['requests_updated']} existing records")

            # Print validation summary
            validation = result.get('validation_summary', {})
            if validation:
                print(f"  Validation: {validation['with_coordinates']}/{validation['total_processed']} requests have coordinates")
                print(f"  Coordinate percentage: {validation['coordinate_percentage']:.1f}%")

            # Print publishing results
            if 'online_publishing' in result:
                online_result = result['online_publishing']
                print(f"\nArcGIS Online Publishing:")
                print(f"  Status: {online_result['status']}")

                if online_result['status'] in ['published', 'updated']:
                    print(f"  Service name: {online_result['service_name']}")
                    print(f"  Service URL: {online_result['service_url']}")
                    print(f"  Action: {online_result['action']}")

                    if 'features_processed' in online_result:
                        print(f"  Features processed: {online_result['features_processed']}")

                elif online_result['status'] == 'error':
                    print(f"  Error: {online_result.get('message', online_result.get('error'))}")

            return 0
        else:
            print(f"\nIntegration failed: {result.get('message', result.get('error', 'Unknown error'))}")
            return 1

    except KeyboardInterrupt:
        print("\nIntegration cancelled by user")
        return 1
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
