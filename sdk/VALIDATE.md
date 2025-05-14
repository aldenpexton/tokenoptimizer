# TokenOptimizer SDK Validation

This document provides instructions for validating the TokenOptimizer SDK before integrating it with external applications like asystant.ai.

## Prerequisites

1. Set up environment variables for API keys:
   ```bash
   export OPENAI_API_KEY=your_openai_key
   export ANTHROPIC_API_KEY=your_anthropic_key 
   export GOOGLE_API_KEY=your_google_key
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements-test.txt
   ```

3. Make sure the backend is either running or can be started by the validation script.

## Running the Validation

The validation script tests all adapters (OpenAI, Anthropic, and Gemini) and simulates integration with external applications.

### Basic Usage

```bash
# Test all providers with backend auto-start
./validate_sdk.py

# Skip starting the backend (if already running)
./validate_sdk.py --skip-backend

# Test only specific providers
./validate_sdk.py --provider openai
./validate_sdk.py --provider anthropic
./validate_sdk.py --provider gemini

# Skip the integration mock test
./validate_sdk.py --skip-mock
```

### Validation Process

The script performs these tests:

1. **Backend Connection**: Verifies the TokenOptimizer backend is running.
2. **OpenAI Adapter**: Tests the OpenAI adapter with a simple completion.
3. **Anthropic Adapter**: Tests the Anthropic adapter with a simple completion.
4. **Gemini Adapter**: Tests the Google Gemini adapter with a simple completion.
5. **asystant.ai Mock Integration**: Simulates how the SDK would be integrated into asystant.ai.

## Interpreting Results

The script will output a summary of all tests. Look for:

- ✅ VALIDATION SUCCESSFUL: SDK is ready for integration
- ❌ VALIDATION FAILED: Issues need to be fixed before integration

## Troubleshooting

If validation fails:

1. **Backend Issues**: Make sure the backend is running and accessible on http://localhost:5000
2. **Missing API Keys**: Verify all required API keys are set as environment variables
3. **Package Dependencies**: Ensure all required packages are installed
4. **Adapter Errors**: Check the specific error messages for each failing adapter

## Integration with asystant.ai

After successful validation, you can integrate the SDK with asystant.ai by:

1. Adding TokenOptimizer SDK as a dependency
2. Importing the `tracked_completion` function
3. Configuring the API endpoint
4. Wrapping your LLM calls with `tracked_completion`

Example:

```python
from tokenoptimizer import tracked_completion
from tokenoptimizer.utils import set_config

# Configure the SDK
set_config(api_url="http://your-backend-url/api/log")

# Use in your asystant.ai application
def get_ai_response(prompt, model):
    # OpenAI example
    if model.startswith("gpt"):
        from openai import OpenAI
        client = OpenAI()
        return tracked_completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            endpoint_name="asystant_ai",  # Track which feature is making the call
            provider_client=client
        )
    # Similar implementation for other providers
```

## Next Steps

Once validation passes, you can proceed to:

1. Integrate the SDK with asystant.ai
2. Set up a production TokenOptimizer backend
3. Build the TokenOptimizer dashboard to view usage data 