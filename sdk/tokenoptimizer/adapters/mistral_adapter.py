"""
Adapter for Mistral AI API.

This module provides an adapter for the Mistral AI API.
"""

from typing import Dict, List, Any, Optional
from .base_adapter import BaseAdapter

class MistralAdapter(BaseAdapter):
    """
    Adapter for Mistral AI API.
    
    This adapter supports the Mistral AI API for Mistral models.
    """
    
    provider_name = "Mistral AI"
    
    def complete(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Any:
        """
        Call the Mistral AI completion API.
        
        Args:
            model: The model to use
            messages: List of message dictionaries
            **kwargs: Additional arguments to pass to the API
            
        Returns:
            Mistral AI API response
        """
        # Check for direct callable chat method
        if hasattr(self.client, "chat") and callable(self.client.chat):
            # Direct chat method
            return self.client.chat(
                model=model,
                messages=messages,
                **kwargs
            )
        # Check for OpenAI-like client format (client.chat.completions.create)
        elif (hasattr(self.client, "chat") and 
              hasattr(self.client.chat, "completions") and 
              hasattr(self.client.chat.completions, "create")):
            # OpenAI-like structure
            return self.client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
        else:
            # Unsupported client format
            raise ValueError("Unsupported Mistral AI client format. Please check your Mistral AI SDK version.")
    
    def extract_usage(self, response: Any) -> Dict[str, int]:
        """
        Extract token usage from Mistral AI response.
        
        Args:
            response: Mistral AI API response
            
        Returns:
            Dict containing prompt_tokens, completion_tokens, and total_tokens
        """
        try:
            # New client format with usage info
            if hasattr(response, "usage"):
                usage = response.usage
                # Handle different attribute names
                if hasattr(usage, "input_tokens"):
                    prompt_tokens = usage.input_tokens
                elif hasattr(usage, "prompt_tokens"):
                    prompt_tokens = usage.prompt_tokens
                else:
                    prompt_tokens = 0
                    
                if hasattr(usage, "output_tokens"):
                    completion_tokens = usage.output_tokens
                elif hasattr(usage, "completion_tokens"):
                    completion_tokens = usage.completion_tokens
                else:
                    completion_tokens = 0
                
                if hasattr(usage, "total_tokens"):
                    total_tokens = usage.total_tokens
                else:
                    total_tokens = prompt_tokens + completion_tokens
                
                return {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens
                }
            # Dict response
            elif isinstance(response, dict) and "usage" in response:
                usage = response["usage"]
                prompt_tokens = usage.get("prompt_tokens", usage.get("input_tokens", 0))
                completion_tokens = usage.get("completion_tokens", usage.get("output_tokens", 0))
                total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)
                return {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens
                }
            # Response without usage info
            else:
                # Mistral doesn't always provide usage info in older versions
                # Fallback to a rough estimation based on content length
                content = ""
                if hasattr(response, "choices") and response.choices:
                    first_choice = response.choices[0]
                    if hasattr(first_choice, "message") and hasattr(first_choice.message, "content"):
                        content = first_choice.message.content
                elif isinstance(response, dict) and "choices" in response:
                    first_choice = response["choices"][0]
                    if "message" in first_choice and "content" in first_choice["message"]:
                        content = first_choice["message"]["content"]
                
                if not isinstance(content, str):
                    content = str(content) if content is not None else ""
                    
                # Very rough token estimation
                prompt_tokens = 0  # We don't know the prompt tokens
                # Ensure we convert to integer
                completion_tokens = int(len(content.split()) * 1.3) if content else 0  # Rough estimate
                total_tokens = prompt_tokens + completion_tokens
                
                return {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens
                }
        except (AttributeError, KeyError, IndexError) as e:
            # Best effort fallback
            return {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            } 