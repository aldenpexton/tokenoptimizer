# TokenOptimizer SDK Integration Guide

This guide walks you through integrating the TokenOptimizer SDK with your existing LLM-powered application. The process is designed to be simple and non-disruptive to your existing code.

## Table of Contents

1. [Installation](#1-installation)
2. [Basic Configuration](#2-basic-configuration)
3. [Integration Examples](#3-integration-examples)
   - [OpenAI](#openai)
   - [Anthropic](#anthropic)
   - [Google Gemini](#google-gemini)
   - [Other Providers](#other-providers)
4. [Advanced Configuration](#4-advanced-configuration)
5. [Troubleshooting](#5-troubleshooting)
6. [Verification](#6-verification)

## 1. Installation

### Local Development

If you're developing locally and have the TokenOptimizer repository:

```bash
# From your application directory
pip install -e /path/to/tokenoptimizer/sdk
```

### Package Installation (Future)

Once the package is published:

```bash
pip install tokenoptimizer
```

### Verify Installation

```python
import tokenoptimizer
print(tokenoptimizer.__version__)  # Should print the current version
```

## 2. Basic Configuration

Add this configuration code at the application startup:

```python
from tokenoptimizer.utils import set_config

# Configure the SDK with your TokenOptimizer backend URL
set_config(
    api_url="http://your-tokenoptimizer-backend:5000/api/log"
)

# Optional: Configure logging
import logging
logging.getLogger("tokenoptimizer").setLevel(logging.INFO)
```

## 3. Integration Examples

### OpenAI

#### Before:
```python
from openai import OpenAI
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Write a short poem"}]
)
```

#### After:
```python
from openai import OpenAI
from tokenoptimizer import tracked_completion

client = OpenAI()

response = tracked_completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "Write a short poem"}],
    endpoint_name="poem_generator",  # Optional: tag to identify this feature
    provider_client=client
)
```

### Anthropic

#### Before:
```python
import anthropic
client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=1000,
    messages=[{"role": "user", "content": "Write a short story"}]
)
```

#### After:
```python
import anthropic
from tokenoptimizer import tracked_completion

client = anthropic.Anthropic()

response = tracked_completion(
    model="claude-3-sonnet-20240229",
    messages=[{"role": "user", "content": "Write a short story"}],
    max_tokens=1000,
    endpoint_name="story_generator",
    provider_client=client
)
```

### Google Gemini

#### Before:
```python
import google.generativeai as genai
genai.configure(api_key="YOUR_API_KEY")

model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("Write a recipe for banana bread")
```

#### After:
```python
import google.generativeai as genai
from tokenoptimizer import tracked_completion

genai.configure(api_key="YOUR_API_KEY")

response = tracked_completion(
    model="gemini-pro",
    messages=[{"role": "user", "content": "Write a recipe for banana bread"}],
    endpoint_name="recipe_generator",
    provider_client=genai
)
```

### Other Providers

The SDK attempts to detect the appropriate adapter based on the model name and client. See the examples folder for more specific provider implementations.

## 4. Advanced Configuration

### Custom Configuration Options

```python
from tokenoptimizer.utils import set_config

set_config(
    api_url="http://your-backend:5000/api/log",
    timeout=5,                   # Custom timeout in seconds
    disable_tracking=False,      # Emergency feature flag to disable tracking
    retry_attempts=3,            # Number of retry attempts for failed logging
    local_logging=True           # Enable local logging as backup
)
```

### Function-Level Configuration

You can override global settings per function call:

```python
response = tracked_completion(
    model="gpt-4",
    messages=[...],
    provider_client=client,
    __tokenoptimizer_config={    # SDK-specific config
        "disable_tracking": True,
        "timeout": 10
    }
)
```

## 5. Troubleshooting

### Common Issues

#### TokenOptimizer Server Unreachable
```
WARNING:tokenoptimizer:Error logging usage: Connection refused
```

**Solution**: Verify the server is running and the URL is correct in your configuration.

#### Unsupported Provider
```
ValueError: Could not detect provider for model: [model-name]
```

**Solution**: Explicitly pass the provider_client parameter or use a supported model name.

#### Missing Token Counts
```
WARNING:tokenoptimizer:Unable to extract token usage from response
```

**Solution**: The provider response format may have changed. Check for SDK updates or use the manual tracking function.

### Manual Tracking

If automatic tracking fails, you can manually track usage:

```python
from tokenoptimizer import track_usage

# Make your LLM call directly
response = client.chat.completions.create(...)

# Then manually track the usage
track_usage(
    model="gpt-4",
    prompt_tokens=response.usage.prompt_tokens,
    completion_tokens=response.usage.completion_tokens,
    total_tokens=response.usage.total_tokens,
    latency_ms=3500,  # You need to measure this yourself
    endpoint_name="my_feature"
)
```

## 6. Verification

After integration, verify data is being logged properly:

1. Make several test requests using your application
2. Check your Supabase database for entries in the `token_logs` table
3. Verify the model, token counts, and costs are recorded correctly

### Query Example (SQL in Supabase):

```sql
SELECT * FROM token_logs
ORDER BY created_at DESC
LIMIT 10;
```

You should see your recent requests with proper token counts and calculated costs.

## Need More Help?

If you encounter issues not covered in this guide:

1. Check the full documentation in the TokenOptimizer repository
2. Look at the example scripts in the `sdk/examples/` directory
3. Run the validation script: `python sdk/validate_sdk.py`
4. Reach out to the TokenOptimizer team for support

---

Good luck with your integration! The TokenOptimizer SDK is designed to be minimally invasive to your existing code while providing valuable insights into your LLM usage. 