#!/usr/bin/env python

"""
Validation script for TokenOptimizer SDK.
Tests each adapter with basic functionality to ensure integration will work.
"""

import os
import sys
import json
import time
import argparse
import subprocess
import requests
from typing import Dict, Any, List, Optional

# Add the parent directory to sys.path to import the SDK
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from tokenoptimizer import tracked_completion
from tokenoptimizer.utils import set_config

# Constants
BACKEND_URL = "http://localhost:5000"
API_ENDPOINT = f"{BACKEND_URL}/api/log"
HEALTH_ENDPOINT = f"{BACKEND_URL}/health"

# Set up the TokenOptimizer SDK configuration
set_config(api_url=API_ENDPOINT)

def check_backend_status() -> bool:
    """Check if the backend server is running."""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def setup_backend() -> subprocess.Popen:
    """Start the backend server if it's not already running."""
    if check_backend_status():
        print("✅ Backend is already running")
        return None
    
    print("Starting backend server...")
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
    process = subprocess.Popen(
        ["python", "app.py"],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for backend to start
    max_attempts = 10
    for i in range(max_attempts):
        if check_backend_status():
            print(f"✅ Backend started successfully on {BACKEND_URL}")
            return process
        print(f"Waiting for backend to start ({i+1}/{max_attempts})...")
        time.sleep(1)
    
    print("❌ Failed to start backend")
    if process:
        process.terminate()
    return None

def test_openai_adapter() -> bool:
    """Test the OpenAI adapter."""
    print("\n===== Testing OpenAI Adapter =====")
    try:
        from openai import OpenAI
    except ImportError:
        print("❌ OpenAI package not installed. Install with: pip install openai")
        return False
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        return False
    
    try:
        client = OpenAI()
        response = tracked_completion(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello in one word."}
            ],
            endpoint_name="validation_test",
            provider_client=client
        )
        print(f"✅ OpenAI adapter test successful")
        print(f"   Response: {response.choices[0].message.content}")
        print(f"   Tokens: {response.usage.total_tokens} total")
        return True
    except Exception as e:
        print(f"❌ OpenAI adapter test failed: {e}")
        return False

def test_anthropic_adapter() -> bool:
    """Test the Anthropic adapter."""
    print("\n===== Testing Anthropic Adapter =====")
    try:
        import anthropic
    except ImportError:
        print("❌ Anthropic package not installed. Install with: pip install anthropic")
        return False
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY environment variable not set")
        return False
    
    try:
        client = anthropic.Anthropic()
        response = tracked_completion(
            model="claude-3-haiku-20240307",
            messages=[
                {"role": "user", "content": "Say hello in one word."}
            ],
            endpoint_name="validation_test",
            provider_client=client
        )
        print(f"✅ Anthropic adapter test successful")
        print(f"   Response: {response.content[0].text}")
        print(f"   Tokens: {response.usage.input_tokens + response.usage.output_tokens} total")
        return True
    except Exception as e:
        print(f"❌ Anthropic adapter test failed: {e}")
        return False

def test_gemini_adapter() -> bool:
    """Test the Gemini adapter."""
    print("\n===== Testing Gemini Adapter =====")
    try:
        import google.generativeai as genai
    except ImportError:
        print("❌ Google Generative AI package not installed. Install with: pip install google-generativeai")
        return False
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY environment variable not set")
        return False
    
    try:
        genai.configure(api_key=api_key)
        response = tracked_completion(
            model="gemini-pro",
            messages=[
                {"role": "user", "content": "Say hello in one word."}
            ],
            endpoint_name="validation_test",
            provider_client=genai
        )
        print(f"✅ Gemini adapter test successful")
        print(f"   Response: {response.text}")
        
        # The usage fields should be available via the GeminiAdapter
        if hasattr(response, 'usage'):
            print(f"   Tokens: {response.usage.total_tokens} total")
        else:
            print("   Note: Token usage not available (expected with Gemini)")
        
        return True
    except Exception as e:
        print(f"❌ Gemini adapter test failed: {e}")
        return False

def mock_asystant_integration() -> bool:
    """Mock integration with asystant.ai."""
    print("\n===== Mocking asystant.ai Integration =====")
    
    # Define a simple mock that would represent your asystant.ai tool
    def mock_asystant_call(prompt: str, model: str):
        """Simulate a call from your asystant.ai tool."""
        try:
            if model.startswith("gpt"):
                # OpenAI model
                from openai import OpenAI
                client = OpenAI()
                return tracked_completion(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    endpoint_name="asystant_ai",
                    provider_client=client
                )
            elif model.startswith("claude"):
                # Anthropic model
                import anthropic
                client = anthropic.Anthropic()
                return tracked_completion(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    endpoint_name="asystant_ai",
                    provider_client=client
                )
            elif model.startswith("gemini"):
                # Google model
                import google.generativeai as genai
                genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
                return tracked_completion(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    endpoint_name="asystant_ai",
                    provider_client=genai
                )
            else:
                raise ValueError(f"Unsupported model: {model}")
        except Exception as e:
            print(f"Error in mock_asystant_call: {e}")
            raise
    
    # Test with each provider
    test_cases = [
        {"prompt": "Write a very brief greeting", "model": "gpt-3.5-turbo"},
        {"prompt": "Write a very brief greeting", "model": "claude-3-haiku-20240307"},
        {"prompt": "Write a very brief greeting", "model": "gemini-pro"}
    ]
    
    success_count = 0
    
    for i, test in enumerate(test_cases):
        print(f"\nTest case {i+1}: {test['model']}")
        
        try:
            response = mock_asystant_call(test["prompt"], test["model"])
            print(f"✅ Successful integration with {test['model']}")
            success_count += 1
        except Exception as e:
            print(f"❌ Failed integration with {test['model']}: {e}")
    
    success_rate = success_count / len(test_cases)
    print(f"\nAsystant.ai mock integration success rate: {success_rate * 100:.1f}%")
    return success_count > 0

def main():
    """Run validation tests for the TokenOptimizer SDK."""
    parser = argparse.ArgumentParser(description='Validate TokenOptimizer SDK')
    parser.add_argument('--skip-backend', action='store_true', help='Skip starting the backend')
    parser.add_argument('--provider', choices=['all', 'openai', 'anthropic', 'gemini'], default='all',
                      help='Which provider to test')
    parser.add_argument('--skip-mock', action='store_true', help='Skip asystant.ai mock integration test')
    args = parser.parse_args()
    
    # Check if backend needs to be started
    backend_process = None
    if not args.skip_backend:
        backend_process = setup_backend()
        if not backend_process and not check_backend_status():
            print("Backend is required for validation. Please start the backend manually or remove --skip-backend")
            return
    
    # Track test results
    results = {
        "openai": False,
        "anthropic": False,
        "gemini": False,
        "mock_integration": False
    }
    
    try:
        # Run provider tests
        if args.provider in ('all', 'openai'):
            results["openai"] = test_openai_adapter()
        
        if args.provider in ('all', 'anthropic'):
            results["anthropic"] = test_anthropic_adapter()
        
        if args.provider in ('all', 'gemini'):
            results["gemini"] = test_gemini_adapter()
        
        # Run mock integration test
        if not args.skip_mock:
            results["mock_integration"] = mock_asystant_integration()
        
        # Print summary
        print("\n===== Validation Summary =====")
        for test, result in results.items():
            if (test == "openai" and args.provider not in ('all', 'openai')) or \
               (test == "anthropic" and args.provider not in ('all', 'anthropic')) or \
               (test == "gemini" and args.provider not in ('all', 'gemini')) or \
               (test == "mock_integration" and args.skip_mock):
                print(f"{test}: Skipped")
            else:
                print(f"{test}: {'✅ Passed' if result else '❌ Failed'}")
        
        # Overall assessment
        tested_items = [r for test, r in results.items() 
                        if (test == "openai" and args.provider in ('all', 'openai')) or
                           (test == "anthropic" and args.provider in ('all', 'anthropic')) or
                           (test == "gemini" and args.provider in ('all', 'gemini')) or
                           (test == "mock_integration" and not args.skip_mock)]
        
        if tested_items and all(tested_items):
            print("\n✅ VALIDATION SUCCESSFUL: SDK is ready for integration with asystant.ai")
        else:
            print("\n❌ VALIDATION FAILED: Please fix the issues before integrating with asystant.ai")
    
    finally:
        # Clean up
        if backend_process:
            print("Shutting down backend...")
            backend_process.terminate()

if __name__ == "__main__":
    main() 