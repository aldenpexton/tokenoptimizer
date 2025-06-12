import requests
import json
from datetime import datetime, timedelta
from tabulate import tabulate
from typing import Dict, Any
import sys

BASE_URL = "http://localhost:5002"

def print_response(endpoint: str, response: Dict[str, Any], show_data: bool = True) -> None:
    """Pretty print the API response"""
    print(f"\n{'='*80}")
    print(f"Testing: {endpoint}")
    print(f"Status Code: {response.get('status_code', 'N/A')}")
    
    if 'error' in response:
        print(f"Error: {response['error']}")
        return
        
    if show_data:
        if isinstance(response, dict):
            print("\nResponse:")
            print(json.dumps(response, indent=2))
        else:
            print("\nResponse (non-JSON):")
            print(response)

def test_health():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/api/health")
    return {
        'status_code': response.status_code,
        **response.json()
    }

def test_filters():
    """Test the filters endpoint"""
    response = requests.get(f"{BASE_URL}/api/filters")
    return {
        'status_code': response.status_code,
        **response.json()
    }

def test_metrics_summary(params=None):
    """Test the metrics summary endpoint"""
    response = requests.get(f"{BASE_URL}/api/metrics/summary", params=params)
    return {
        'status_code': response.status_code,
        **response.json()
    }

def test_metrics_by_model(params=None):
    """Test the metrics by model endpoint"""
    response = requests.get(f"{BASE_URL}/api/metrics/by-model", params=params)
    return {
        'status_code': response.status_code,
        **response.json()
    }

def test_metrics_by_endpoint(params=None):
    """Test the metrics by endpoint endpoint"""
    response = requests.get(f"{BASE_URL}/api/metrics/by-endpoint", params=params)
    return {
        'status_code': response.status_code,
        **response.json()
    }

def test_metrics_trend(params=None):
    """Test the metrics trend endpoint"""
    response = requests.get(f"{BASE_URL}/api/metrics/trend", params=params)
    return {
        'status_code': response.status_code,
        **response.json()
    }

def test_recommendations(params=None):
    """Test the recommendations endpoint"""
    response = requests.get(f"{BASE_URL}/api/recommendations", params=params)
    return {
        'status_code': response.status_code,
        **response.json()
    }

def test_logs(params=None):
    """Test the logs endpoint"""
    response = requests.get(f"{BASE_URL}/api/logs", params=params)
    return {
        'status_code': response.status_code,
        **response.json()
    }

def test_logs_csv_export(params=None):
    """Test the logs CSV export"""
    if params is None:
        params = {}
    params['format'] = 'csv'
    
    try:
        response = requests.get(f"{BASE_URL}/api/logs", params=params)
        if response.status_code == 200:
            return {
                'status_code': response.status_code,
                'content_type': response.headers.get('Content-Type'),
                'content_disposition': response.headers.get('Content-Disposition'),
                'data': response.text[:200] + '...' if len(response.text) > 200 else response.text
            }
        else:
            return {
                'status_code': response.status_code,
                'error': 'Failed to export CSV'
            }
    except Exception as e:
        return {
            'status_code': 500,
            'error': f'Error exporting CSV: {str(e)}'
        }

def run_basic_tests():
    """Run basic tests without parameters"""
    print("\nRunning basic endpoint tests...")
    
    # Test health check
    print_response("/api/health", test_health())
    
    # Test filters
    print_response("/api/filters", test_filters())
    
    # Test metrics endpoints
    print_response("/api/metrics/summary", test_metrics_summary())
    print_response("/api/metrics/by-model", test_metrics_by_model())
    print_response("/api/metrics/by-endpoint", test_metrics_by_endpoint())
    print_response("/api/metrics/trend", test_metrics_trend())
    
    # Test recommendations
    print_response("/api/recommendations", test_recommendations())
    
    # Test logs
    print_response("/api/logs", test_logs())
    
    # Test CSV export
    print_response("/api/logs (CSV)", test_logs_csv_export(), show_data=False)

def run_filter_tests():
    """Run tests with different filter combinations"""
    print("\nRunning filter combination tests...")
    
    # Test different time granularities
    granularities = ['hour', 'day', 'week', 'month', 'year']
    for granularity in granularities:
        params = {'granularity': granularity}
        print_response(
            f"/api/metrics/trend (granularity={granularity})", 
            test_metrics_trend(params)
        )
    
    # Test with specific date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    params = {
        'granularity': 'day',
        'end_date': end_date.isoformat()
    }
    print_response(
        "/api/metrics/summary (with date range)", 
        test_metrics_summary(params)
    )
    
    # Get available filters
    filters = test_filters()
    
    # Test with model filter
    if filters.get('models'):
        params = {'model': filters['models'][0]}
        print_response(
            f"/api/metrics/by-model (model={params['model']})", 
            test_metrics_by_model(params)
        )
    
    # Test with endpoint filter
    if filters.get('endpoints'):
        params = {'endpoint': filters['endpoints'][0]}
        print_response(
            f"/api/metrics/by-endpoint (endpoint={params['endpoint']})", 
            test_metrics_by_endpoint(params)
        )
    
    # Test combined filters
    if filters.get('models') and filters.get('endpoints'):
        params = {
            'granularity': 'day',
            'model': filters['models'][0],
            'endpoint': filters['endpoints'][0]
        }
        print_response(
            "Combined filters test", 
            test_metrics_summary(params)
        )

def run_pagination_tests():
    """Run tests for pagination and sorting"""
    print("\nRunning pagination and sorting tests...")
    
    # Test different page sizes
    params = {'per_page': 10}
    print_response("/api/logs (page_size=10)", test_logs(params))
    
    # Test invalid page size
    params = {'per_page': -1}
    print_response("/api/logs (invalid page size)", test_logs(params))
    
    # Test invalid page number
    params = {'page': 0}
    print_response("/api/logs (invalid page)", test_logs(params))
    
    # Test sorting
    params = {'sort_by': 'total_cost', 'sort_desc': 'true'}
    print_response("/api/logs (sorted by cost)", test_logs(params))
    
    # Test invalid sort field
    params = {'sort_by': 'invalid_field'}
    print_response("/api/logs (invalid sort field)", test_logs(params))

def run_error_tests():
    """Run tests for error cases"""
    print("\nRunning error case tests...")
    
    # Test invalid date format
    params = {'end_date': 'invalid-date'}
    print_response("/api/metrics/summary (invalid date)", test_metrics_summary(params))
    
    # Test invalid granularity
    params = {'granularity': 'invalid'}
    print_response("/api/metrics/trend (invalid granularity)", test_metrics_trend(params))
    
    # Test non-existent model
    params = {'model': ['non-existent-model']}
    print_response("/api/metrics/by-model (non-existent model)", test_metrics_by_model(params))
    
    # Test non-existent endpoint
    params = {'endpoint': ['non-existent-endpoint']}
    print_response("/api/metrics/by-endpoint (non-existent endpoint)", test_metrics_by_endpoint(params))
    
    # Test invalid provider
    params = {'provider': ['invalid-provider']}
    print_response("/api/metrics/summary (invalid provider)", test_metrics_summary(params))

def main():
    """Main test runner"""
    try:
        # Check if server is running
        health = test_health()
        if health.get('status_code') != 200:
            print("Error: Backend server is not running!")
            sys.exit(1)
            
        print("\nBackend server is running!")
        
        # Run all test suites
        run_basic_tests()
        run_filter_tests()
        run_pagination_tests()
        run_error_tests()
        
        print("\nAll tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the backend server!")
        print("Please make sure the server is running on http://localhost:5002")
        sys.exit(1)
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 