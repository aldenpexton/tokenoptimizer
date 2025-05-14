"""
Adapters for different LLM providers.

This package provides adapters for different LLM providers (OpenAI, Anthropic, etc.)
to standardize the API and token usage extraction.
"""

from typing import Any, Dict, Optional

from .base_adapter import BaseAdapter
from .openai_adapter import OpenAIAdapter
from .anthropic_adapter import AnthropicAdapter
from .mistral_adapter import MistralAdapter
from .gemini_adapter import GeminiAdapter

def get_adapter(model: str, client: Any) -> BaseAdapter:
    """
    Get the appropriate adapter for the given model and client.
    
    Args:
        model: The model name
        client: The provider client instance
        
    Returns:
        An adapter instance for the provider
        
    Raises:
        ValueError: If no adapter is found for the model or client
    """
    # Detect provider based on client type
    client_module = client.__class__.__module__ if hasattr(client, "__class__") else None
    client_class = client.__class__.__name__ if hasattr(client, "__class__") else None
    
    # Check for OpenAI
    if model.startswith("gpt") or (client_module and "openai" in client_module.lower()):
        return OpenAIAdapter(client)
        
    # Check for Anthropic
    if model.startswith("claude") or (client_module and "anthropic" in client_module.lower()):
        return AnthropicAdapter(client)
        
    # Check for Mistral
    if model.startswith("mistral") or (client_module and "mistral" in client_module.lower()):
        return MistralAdapter(client)
        
    # Check for Gemini
    if (model.startswith("gemini") or 
        (client_module and ("google" in client_module.lower() or "genai" in client_module.lower()))):
        return GeminiAdapter(client)
        
    # Fallback to exception
    raise ValueError(f"No adapter found for model {model} with client {client_class}")

__all__ = ['get_adapter', 'BaseAdapter', 'OpenAIAdapter', 'AnthropicAdapter', 'MistralAdapter', 'GeminiAdapter'] 