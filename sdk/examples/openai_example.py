"""
Example usage of TokenOptimizer SDK with OpenAI.
"""

import os
import sys
import time

# Add the parent directory to sys.path to import the SDK
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the SDK
from tokenoptimizer import tracked_completion
from tokenoptimizer.utils import set_config

# Set the API URL to point to your TokenOptimizer backend
set_config(api_url="http://localhost:5000/api/log")

def main():
    """
    Example of using TokenOptimizer SDK with OpenAI.
    """
    try:
        from openai import OpenAI
    except ImportError:
        print("OpenAI package not installed. Install with: pip install openai")
        return

    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY environment variable not set.")
        return

    # Initialize the OpenAI client
    client = OpenAI()

    print("Sending request to OpenAI with TokenOptimizer tracking...")
    
    # Measure latency for comparison
    start_time = time.time()
    
    # Make the API call using TokenOptimizer SDK
    response = tracked_completion(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Write a short paragraph about AI optimization."}
        ],
        endpoint_name="example",  # Tag for this specific endpoint/feature
        provider_client=client
    )
    
    # Calculate total time
    total_time = (time.time() - start_time) * 1000  # ms
    
    # Display results
    print("\n===== RESULTS =====")
    print(f"Response: {response.choices[0].message.content}")
    print(f"Tokens: {response.usage.prompt_tokens} prompt + {response.usage.completion_tokens} completion = {response.usage.total_tokens} total")
    print(f"Actual latency: {total_time:.2f}ms")
    print("====================\n")
    
    print("TokenOptimizer has logged this request to your dashboard.")

if __name__ == "__main__":
    main() 