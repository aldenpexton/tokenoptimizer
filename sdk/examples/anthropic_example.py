"""
Example usage of TokenOptimizer SDK with Anthropic.
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
    Example of using TokenOptimizer SDK with Anthropic.
    """
    try:
        from anthropic import Anthropic
    except ImportError:
        print("Anthropic package not installed. Install with: pip install anthropic")
        return

    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ANTHROPIC_API_KEY environment variable not set.")
        return

    # Initialize the Anthropic client
    client = Anthropic()

    print("Sending request to Anthropic with TokenOptimizer tracking...")
    
    # Measure latency for comparison
    start_time = time.time()
    
    # Make the API call using TokenOptimizer SDK
    response = tracked_completion(
        model="claude-3-haiku",
        messages=[
            {"role": "user", "content": "Explain how transformers work in machine learning."}
        ],
        endpoint_name="education",  # Tag for this specific endpoint/feature
        provider_client=client,
        max_tokens=300  # Additional parameters pass through to the API
    )
    
    # Calculate total time
    total_time = (time.time() - start_time) * 1000  # ms
    
    # Display results
    print("\n===== RESULTS =====")
    
    # Handle different response formats
    if hasattr(response, "content") and isinstance(response.content, list):
        content = response.content[0].text
    elif hasattr(response, "content"):
        content = response.content
    else:
        content = str(response)
        
    print(f"Response: {content}")
    
    # Extract usage if available
    if hasattr(response, "usage"):
        print(f"Tokens: {response.usage.input_tokens} input + {response.usage.output_tokens} output = {response.usage.input_tokens + response.usage.output_tokens} total")
    
    print(f"Actual latency: {total_time:.2f}ms")
    print("====================\n")
    
    print("TokenOptimizer has logged this request to your dashboard.")

if __name__ == "__main__":
    main() 