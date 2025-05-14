# Integrating TokenOptimizer with asystant.ai

This guide provides step-by-step instructions for integrating the TokenOptimizer SDK with asystant.ai to track token usage across all LLM providers.

## Prerequisites

Before integrating TokenOptimizer with asystant.ai, you'll need:

1. A working TokenOptimizer backend server
2. TokenOptimizer SDK installed (either from PyPI or your private package repository)
3. API keys for the LLM providers you're using (OpenAI, Anthropic, Gemini)

## Installation

Install the TokenOptimizer SDK:

```bash
# If published to PyPI
pip install tokenoptimizer

# Or install from a local directory
pip install -e /path/to/tokenoptimizer/sdk
```

## Integration Steps

### 1. Configure the SDK

At application startup, configure the TokenOptimizer SDK with your backend URL:

```python
from tokenoptimizer.utils import set_config

# For production, this should point to your hosted TokenOptimizer backend
TOKENOPTIMIZER_API_URL = "https://your-tokenoptimizer-instance.com/api/log"

# Configure the SDK
set_config(api_url=TOKENOPTIMIZER_API_URL)
```

### 2. Update LLM Call Functions

Modify your existing LLM call functions to use the `tracked_completion` wrapper.

**Example for OpenAI:**

```python
# Before:
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello, how are you?"}]
)

# After:
from tokenoptimizer import tracked_completion
from openai import OpenAI

client = OpenAI()
response = tracked_completion(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello, how are you?"}],
    endpoint_name="chat_feature",  # Identify which part of your app is making the call
    provider_client=client
)
```

**Example for Anthropic:**

```python
# Before:
from anthropic import Anthropic
client = Anthropic()
response = client.messages.create(
    model="claude-3-haiku-20240307",
    messages=[{"role": "user", "content": "Hello, how are you?"}]
)

# After:
from tokenoptimizer import tracked_completion
from anthropic import Anthropic

client = Anthropic()
response = tracked_completion(
    model="claude-3-haiku-20240307",
    messages=[{"role": "user", "content": "Hello, how are you?"}],
    endpoint_name="chat_feature",
    provider_client=client
)
```

**Example for Gemini:**

```python
# Before:
import google.generativeai as genai
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("Hello, how are you?")

# After:
from tokenoptimizer import tracked_completion
import google.generativeai as genai

genai.configure(api_key=api_key)
response = tracked_completion(
    model="gemini-pro",
    messages=[{"role": "user", "content": "Hello, how are you?"}],
    endpoint_name="chat_feature",
    provider_client=genai
)
```

### 3. Handling Multi-Provider Support

If your application supports multiple LLM providers, you can create a unified function:

```python
def generate_response(prompt, model, system_prompt=None, feature_name="default"):
    """Generate a response using any supported LLM provider with token tracking."""
    # Determine provider based on model name
    if model.startswith("gpt"):
        from openai import OpenAI
        client = OpenAI()
    elif model.startswith("claude"):
        from anthropic import Anthropic
        client = Anthropic()
    elif model.startswith("gemini"):
        import google.generativeai as genai
        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
        client = genai
    else:
        raise ValueError(f"Unsupported model: {model}")
    
    # Prepare messages
    messages = []
    if system_prompt and not model.startswith("gemini"):
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    # Make the tracked call
    return tracked_completion(
        model=model,
        messages=messages,
        endpoint_name=feature_name,
        provider_client=client
    )
```

### 4. Best Practices

For optimal integration with asystant.ai:

1. **Track features separately**: Use distinct `endpoint_name` values for different features to see which parts of your app use the most tokens
2. **Handle errors gracefully**: The TokenOptimizer SDK is designed to never break your application, but always wrap calls in try/except blocks
3. **Access token counts**: Use the appropriate response field to access token counts based on the provider:
   - OpenAI: `response.usage.total_tokens`
   - Anthropic: `response.usage.input_tokens + response.usage.output_tokens`
   - Gemini: `response.usage.total_tokens` (added by TokenOptimizer)

## Full Integration Example

See `examples/asystant_integration.py` for a complete example of integrating TokenOptimizer with a multi-provider application similar to asystant.ai.

## Testing the Integration

Before deploying to production, run the validation script to ensure everything works correctly:

```bash
# From the SDK directory
./validate_sdk.py
```

## Support

If you encounter any issues with the integration:

1. Check the validation results
2. Verify your backend is running correctly
3. Ensure you have the latest version of the SDK
4. Contact the TokenOptimizer team for support

## Next Steps

After successful integration:

1. Check your TokenOptimizer dashboard to view token usage data
2. Analyze usage patterns to optimize your prompts and models
3. Set up alerts for unusual token usage or cost spikes 