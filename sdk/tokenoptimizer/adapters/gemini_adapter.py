"""
Adapter for Google's Gemini API.

This module provides an adapter for the Google Gemini API.
"""

from typing import Dict, List, Any, Optional, cast
from .base_adapter import BaseAdapter

class GeminiAdapter(BaseAdapter):
    """
    Adapter for Google Gemini API.
    
    This adapter supports the Google Gemini API for Gemini models.
    """
    
    provider_name = "Google"
    
    def complete(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Any:
        """
        Call the Gemini completion API.
        
        Args:
            model: The model to use
            messages: List of message dictionaries
            **kwargs: Additional arguments to pass to the API
            
        Returns:
            Gemini API response
        """
        # Check for the newer genai client format
        if hasattr(self.client, "generate_content"):
            # Convert messages to Gemini format if needed
            gemini_messages = []
            
            for msg in messages:
                if msg["role"] == "user":
                    gemini_messages.append({"role": "user", "parts": [{"text": msg["content"]}]})
                elif msg["role"] == "assistant":
                    gemini_messages.append({"role": "model", "parts": [{"text": msg["content"]}]})
                elif msg["role"] == "system":
                    # System messages can be handled as special user messages in Gemini
                    gemini_messages.insert(0, {"role": "user", "parts": [{"text": msg["content"]}]})
            
            return self.client.generate_content(
                gemini_messages,
                generation_config=kwargs.get("generation_config", None),
                safety_settings=kwargs.get("safety_settings", None)
            )
        # Check for the chat method (alternative format)
        elif hasattr(self.client, "chat") and callable(self.client.chat):
            return self.client.chat(
                model=model,
                messages=messages,
                **kwargs
            )
        else:
            raise ValueError("Unsupported Google Gemini client format. Please check your Gemini SDK version.")
    
    def extract_usage(self, response: Any) -> Dict[str, int]:
        """
        Extract token usage from Gemini response.
        
        Args:
            response: Gemini API response
            
        Returns:
            Dict containing prompt_tokens, completion_tokens, and total_tokens
        """
        try:
            # Check for usage_metadata (common in Gemini responses)
            if hasattr(response, "usage_metadata"):
                usage = response.usage_metadata
                prompt_tokens = getattr(usage, "prompt_token_count", 0)
                completion_tokens = getattr(usage, "candidates_token_count", 0)
                
                return {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                }
            # Check for dictionary response format
            elif isinstance(response, dict) and "usage_metadata" in response:
                usage = response["usage_metadata"]
                prompt_tokens = usage.get("prompt_token_count", 0)
                completion_tokens = usage.get("candidates_token_count", 0)
                
                return {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                }
            # Check for standard usage format (like OpenAI)
            elif hasattr(response, "usage"):
                # Cast response to Any to avoid dict type checking error
                response_obj = cast(Any, response)
                usage = response_obj.usage
                
                # Try to extract tokens with different naming patterns
                prompt_tokens = getattr(usage, "prompt_tokens", getattr(usage, "input_tokens", 0))
                completion_tokens = getattr(usage, "completion_tokens", getattr(usage, "output_tokens", 0))
                total_tokens = getattr(usage, "total_tokens", prompt_tokens + completion_tokens)
                
                return {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens
                }
            # Fallback - try to estimate from text content
            else:
                # For testing or when we can't get real token counts
                text = ""
                if hasattr(response, "text"):
                    # Cast response to Any to avoid dict type checking error
                    response_obj = cast(Any, response)
                    text = str(response_obj.text)
                    
                # Very rough estimation based on length of text
                if text:
                    completion_tokens = int(len(text.split()) * 1.3)  # Rough estimate
                else:
                    completion_tokens = 0
                    
                return {
                    "prompt_tokens": 0,  # Can't estimate prompt tokens
                    "completion_tokens": completion_tokens,
                    "total_tokens": completion_tokens
                }
        except (AttributeError, KeyError, IndexError):
            # Best effort fallback
            return {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            } 