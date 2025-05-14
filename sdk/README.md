# TokenOptimizer SDK

A Python SDK for tracking and optimizing LLM API usage, costs, and performance.

## Installation

```bash
pip install tokenoptimizer
```

Or install with specific provider support:

```bash
pip install tokenoptimizer[openai]     # For OpenAI support
pip install tokenoptimizer[anthropic]  # For Anthropic support
pip install tokenoptimizer[mistral]    # For Mistral support
pip install tokenoptimizer[all]        # For all providers
```

## Usage

### Basic Usage with OpenAI

```python
from tokenoptimizer import tracked_completion
from openai import OpenAI

client = OpenAI()

# Wrap your existing completions call with tracked_completion
response = tracked_completion(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Generate a short poem about AI."}
    ],
    endpoint_name="poetry_generator",  # Optional tag for your feature/endpoint
    provider_client=client
)

# Use the response as you normally would
print(response.choices[0].message.content)
```

### Basic Usage with Anthropic

```python
from tokenoptimizer import tracked_completion
from anthropic import Anthropic

client = Anthropic()

response = tracked_completion(
    model="claude-3-haiku",
    messages=[
        {"role": "user", "content": "Explain quantum computing in simple terms."}
    ],
    endpoint_name="explanations",  # Optional tag for your feature/endpoint
    provider_client=client
)

print(response.content)
```

### Manually Tracking Usage

If you need more control or want to track usage manually:

```python
from tokenoptimizer import track_usage

# After making your API call and retrieving response
track_usage(
    model="gpt-4",
    prompt_tokens=150,
    completion_tokens=50,
    total_tokens=200,
    latency_ms=1200,
    endpoint_name="summarization"
)
```

### Configuration

You can configure the SDK with:

```python
from tokenoptimizer.utils import set_config

set_config(
    api_url="https://your-tokenoptimizer-api.com/api/log",
    timeout=5,  # Request timeout in seconds
    debug=True  # Enable debug mode
)
```

Or use environment variables:

```
TOKENOPTIMIZER_API_URL=https://your-tokenoptimizer-api.com/api/log
TOKENOPTIMIZER_DEBUG=true
```

## Features

- 📊 Track token usage, latency, and model selection
- 💰 Calculate estimated costs based on latest pricing
- 🔄 Zero-latency integration with existing code
- 🧩 Support for multiple LLM providers (OpenAI, Anthropic, Mistral)

## Supported Providers

- ✅ OpenAI (gpt-3.5-turbo, gpt-4, etc.)
- ✅ Anthropic (claude-3-opus, claude-3-sonnet, claude-3-haiku, etc.)
- ✅ Mistral AI (mistral-small, mistral-medium, mistral-large, etc.)

## License

This project is licensed under the MIT License - see the LICENSE file for details. 