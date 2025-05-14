#!/usr/bin/env python

"""
Simple test script for TokenOptimizer backend API.
This script makes a direct API call to the backend without requiring LLM API keys.
"""

import requests
import json
import time
from datetime import datetime

# API endpoint
API_URL = "http://localhost:5000/api/log"

def test_direct_api_call():
    """Test the API directly with a mock payload"""
    
    # Create a mock LLM usage payload
    payload = {
        "model": "gpt-3.5-turbo",
        "prompt_tokens": 100,
        "completion_tokens": 50,
        "total_tokens": 150,
        "latency_ms": 500,
        "endpoint_name": "direct_test",
        "timestamp": datetime.now().isoformat(),
        "api_provider": "OpenAI"
    }
    
    print(f"Sending test payload to {API_URL}:")
    print(json.dumps(payload, indent=2))
    
    # Send request to the API
    try:
        start_time = time.time()
        response = requests.post(API_URL, json=payload)
        duration = (time.time() - start_time) * 1000  # ms
        
        print(f"\nRequest completed in {duration:.2f}ms")
        
        if response.status_code == 201:
            print("✅ SUCCESS: Token usage logged successfully")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"❌ ERROR: API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_direct_api_call()
    print("\n=== TEST SUMMARY ===")
    if success:
        print("✅ Backend API is working correctly")
        print("✅ Check your Supabase dashboard to verify data was stored")
    else:
        print("❌ Test failed. Please check backend logs for details") 