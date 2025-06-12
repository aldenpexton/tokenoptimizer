"""
Core functionality for the TokenOptimizer SDK.

This module provides the main tracking functions for LLM API calls.
"""

import time
import json
import logging
import datetime
import requests
from typing import Dict, List, Any, Optional, Union, Callable

from .utils.validation import validate_input, validate_messages
from .utils.config import get_config

# Set up logging
logger = logging.getLogger("tokenoptimizer")

def track_usage(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    latency_ms: float,
    endpoint_name: str = "default",
    timestamp: Optional[str] = None,
    api_provider: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Track token usage and latency for an LLM API call.
    
    Args:
        model: The model used (e.g., "gpt-4", "claude-3-haiku")
        prompt_tokens: Number of input tokens
        completion_tokens: Number of output tokens
        total_tokens: Total tokens used
        latency_ms: Request latency in milliseconds
        endpoint_name: Optional name/tag for the endpoint or feature
        timestamp: Optional ISO timestamp (default: current time)
        api_provider: Optional provider name (default: inferred from model)
        
    Returns:
        Dict containing the logged information and status
    """
    # Validate inputs
    validate_input(model=model, prompt_tokens=prompt_tokens, 
                  completion_tokens=completion_tokens, total_tokens=total_tokens)
    
    # Get config
    config = get_config()
    api_url = config.get("api_url", "http://localhost:5002/api/log")
    
    # Prepare timestamp
    if not timestamp:
        timestamp = datetime.datetime.now().isoformat()
        
    # Infer API provider if not provided
    if not api_provider:
        if model.startswith("gpt"):
            api_provider = "OpenAI"
        elif model.startswith("claude"):
            api_provider = "Anthropic"
        elif model.startswith("mistral"):
            api_provider = "Mistral AI"
        else:
            api_provider = "Unknown"
    
    # Prepare payload
    payload = {
        "model": model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "latency_ms": latency_ms,
        "endpoint_name": endpoint_name,
        "timestamp": timestamp,
        "api_provider": api_provider
    }
    
    # Send data to TokenOptimizer API
    try:
        response = requests.post(url=api_url, json=payload, timeout=3)
        if response.status_code == 201:
            logger.debug(f"TokenOptimizer: Successfully logged usage for {model}")
            return {"success": True, "log": response.json()["log"]}
        else:
            logger.warning(f"TokenOptimizer: Failed to log usage. Status: {response.status_code}")
            return {"success": False, "error": f"API error: {response.status_code}"}
    except Exception as e:
        logger.warning(f"TokenOptimizer: Error logging usage: {str(e)}")
        return {"success": False, "error": str(e)}
        
def tracked_completion(
    model: str,
    messages: List[Dict[str, str]],
    endpoint_name: str = "default",
    provider_client: Any = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Track an LLM completion call and log its token usage.
    
    This is a wrapper around the provider's completion API that automatically
    tracks token usage, latency, and cost.
    
    Args:
        model: The model to use (e.g., "gpt-4", "claude-3-haiku")
        messages: List of message dictionaries with role and content
        endpoint_name: Optional name/tag for the endpoint or feature
        provider_client: The client instance (OpenAI, Anthropic, etc.)
        **kwargs: Additional arguments to pass to the provider's API
        
    Returns:
        The original provider response
    """
    # If no provider_client is provided, try to detect provider from model
    if provider_client is None:
        provider_client = _detect_provider_from_model(model)
        
    # Record start time
    start_time = time.time()
    
    # Call the provider's completion API
    from .adapters import get_adapter
    adapter = get_adapter(model, provider_client)
    response = adapter.complete(model, messages, **kwargs)
    
    # Calculate latency
    latency_ms = (time.time() - start_time) * 1000
    
    # Extract token usage
    usage = adapter.extract_usage(response)
    
    # Track the usage
    track_usage(
        model=model,
        prompt_tokens=usage["prompt_tokens"],
        completion_tokens=usage["completion_tokens"],
        total_tokens=usage["total_tokens"],
        latency_ms=latency_ms,
        endpoint_name=endpoint_name,
        api_provider=adapter.provider_name
    )
    
    # Return the original response
    return response

def _detect_provider_from_model(model: str) -> Any:
    """
    Attempt to detect and initialize the appropriate provider client based on model name.
    
    This is a fallback when no provider_client is passed, but should be used cautiously
    as it makes assumptions about available packages.
    """
    if model.startswith("gpt"):
        try:
            import openai
            return openai.OpenAI()
        except (ImportError, AttributeError):
            try:
                import openai
                return openai
            except ImportError:
                raise ImportError("OpenAI package not found. Please install with: pip install openai")
    
    elif model.startswith("claude"):
        try:
            import anthropic
            return anthropic.Anthropic()
        except ImportError:
            raise ImportError("Anthropic package not found. Please install with: pip install anthropic")
            
    elif model.startswith("mistral"):
        try:
            import mistralai.client
            return mistralai.client.MistralClient()
        except ImportError:
            raise ImportError("Mistral AI package not found. Please install with: pip install mistralai")
            
    else:
        raise ValueError(f"Could not detect provider for model: {model}. Please provide provider_client explicitly.")

def get_adapter(model: str, client: Any) -> Any:
    """
    Import and get the appropriate adapter for the given model and client.
    
    This function exists to solve the circular import issue between core and adapters.
    
    Args:
        model: The model name
        client: The provider client instance
        
    Returns:
        An adapter instance for the provider
    """
    from .adapters import get_adapter as get_adapter_impl
    return get_adapter_impl(model, client) 