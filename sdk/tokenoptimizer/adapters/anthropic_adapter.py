"""
Adapter for Anthropic API.

This module provides an adapter for the Anthropic API.
"""

from typing import Dict, List, Any, Optional
from .base_adapter import BaseAdapter

class AnthropicAdapter(BaseAdapter):
    """
    Adapter for Anthropic API.
    
    This adapter supports the Anthropic API for Claude models.
    """
    
    provider_name = "Anthropic"
    
    def complete(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Any:
        """
        Call the Anthropic completion API.
        
        Args:
            model: The model to use
            messages: List of message dictionaries
            **kwargs: Additional arguments to pass to the API
            
        Returns:
            Anthropic API response
        """
        # Check for newer client format (>= v0.10.0)
        if hasattr(self.client, "messages") and hasattr(self.client.messages, "create"):
            # Use the messages API
            return self.client.messages.create(
                model=model,
                messages=messages,
                **kwargs
            )
        # Check for legacy client format (< v0.10.0)
        elif hasattr(self.client, "completions") and hasattr(self.client.completions, "create"):
            # Convert messages to Anthropic format
            # For older versions, convert chat format to prompt format
            system_message = None
            conversation = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                elif msg["role"] == "user":
                    conversation.append({"role": "human", "content": msg["content"]})
                elif msg["role"] == "assistant":
                    conversation.append({"role": "assistant", "content": msg["content"]})
            
            # Create the completion request
            request_args = {"model": model, **kwargs}
            
            if system_message:
                request_args["system"] = system_message
                
            if "max_tokens" not in kwargs and "max_tokens_to_sample" not in kwargs:
                request_args["max_tokens_to_sample"] = 1000  # Default
                
            if conversation:
                return self.client.completions.create(**request_args)
            else:
                raise ValueError("No valid messages found for Anthropic completion")
        else:
            raise ValueError("Unsupported Anthropic client format. Please update to the latest version.")
    
    def extract_usage(self, response: Any) -> Dict[str, int]:
        """
        Extract token usage from Anthropic response.
        
        Args:
            response: Anthropic API response
            
        Returns:
            Dict containing prompt_tokens, completion_tokens, and total_tokens
        """
        try:
            # New client format
            if hasattr(response, "usage"):
                usage = response.usage
                return {
                    "prompt_tokens": usage.input_tokens,
                    "completion_tokens": usage.output_tokens,
                    "total_tokens": usage.input_tokens + usage.output_tokens
                }
            # Dict response (some API versions)
            elif isinstance(response, dict) and "usage" in response:
                usage = response["usage"]
                input_tokens = usage.get("input_tokens", 0)
                output_tokens = usage.get("output_tokens", 0)
                return {
                    "prompt_tokens": input_tokens,
                    "completion_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens
                }
            # Legacy format without usage info - estimate based on content
            else:
                # Anthropic doesn't always provide token counts, especially in older versions
                # For older versions, we'll provide an estimation based on a simple heuristic
                # Note: This is a rough approximation
                content = ""
                if hasattr(response, "content") and response.content:
                    if isinstance(response.content, list) and response.content and hasattr(response.content[0], "text"):
                        content = response.content[0].text
                    elif isinstance(response.content, str):
                        content = response.content
                    else:
                        content = str(response.content)
                elif isinstance(response, dict) and "completion" in response:
                    content = response["completion"]
                    
                # Very rough token estimation
                prompt_tokens = 0
                # Ensure we're working with a string and convert to an integer approximation
                if isinstance(content, str):
                    completion_tokens = int(len(content.split()) * 1.3)  # Rough estimate
                else:
                    completion_tokens = 0
                
                return {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                }
        except (AttributeError, KeyError) as e:
            # Best effort fallback
            return {
                "prompt_tokens": 0, 
                "completion_tokens": 0,
                "total_tokens": 0
            } 