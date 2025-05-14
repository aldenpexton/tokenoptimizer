"""
Adapter for OpenAI API.

This module provides an adapter for the OpenAI API.
"""

from typing import Dict, List, Any, Optional
from .base_adapter import BaseAdapter

class OpenAIAdapter(BaseAdapter):
    """
    Adapter for OpenAI API.
    
    This adapter supports both the new (client-based) and legacy OpenAI APIs.
    """
    
    provider_name = "OpenAI"
    
    def complete(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Any:
        """
        Call the OpenAI completion API.
        
        Args:
            model: The model to use
            messages: List of message dictionaries
            **kwargs: Additional arguments to pass to the API
            
        Returns:
            OpenAI API response
        """
        # Determine if we're using the new client-based API or the legacy API
        if hasattr(self.client, "chat") and hasattr(self.client.chat, "completions"):
            # New client-based API (openai>=1.0.0)
            return self.client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
        elif hasattr(self.client, "ChatCompletion") and hasattr(self.client.ChatCompletion, "create"):
            # Legacy API (openai<1.0.0)
            return self.client.ChatCompletion.create(
                model=model,
                messages=messages,
                **kwargs
            )
        else:
            # Fallback for even older versions or unexpected client format
            raise ValueError("Unsupported OpenAI client format. Please update to the latest version.")
    
    def extract_usage(self, response: Any) -> Dict[str, int]:
        """
        Extract token usage from OpenAI response.
        
        Args:
            response: OpenAI API response
            
        Returns:
            Dict containing prompt_tokens, completion_tokens, and total_tokens
        """
        # Handle different response formats
        try:
            # New client-based API (openai>=1.0.0)
            if hasattr(response, "usage"):
                usage = response.usage
                return {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                }
            # Legacy API (openai<1.0.0)
            elif isinstance(response, dict) and "usage" in response:
                usage = response["usage"]
                return {
                    "prompt_tokens": usage["prompt_tokens"],
                    "completion_tokens": usage["completion_tokens"],
                    "total_tokens": usage["total_tokens"]
                }
            else:
                raise ValueError("Could not extract token usage from OpenAI response")
        except (AttributeError, KeyError) as e:
            raise ValueError(f"Error extracting token usage from OpenAI response: {str(e)}") 