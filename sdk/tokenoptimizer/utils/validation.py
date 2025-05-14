"""
Input validation for the TokenOptimizer SDK.

This module provides functions to validate input data.
"""

from typing import Dict, Any, Tuple, Optional, Union

def validate_input(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    latency_ms: Optional[float] = None,
    endpoint_name: Optional[str] = None
) -> None:
    """
    Validate the input data for token tracking.
    
    Args:
        model: Model name
        prompt_tokens: Number of input tokens
        completion_tokens: Number of output tokens
        total_tokens: Total tokens used
        latency_ms: Request latency in milliseconds (optional)
        endpoint_name: Endpoint or feature name (optional)
        
    Raises:
        ValueError: If any validation check fails
    """
    # Check model name
    if not model or not isinstance(model, str):
        raise ValueError("Model name must be a non-empty string")
    
    # Check token counts
    if not isinstance(prompt_tokens, int) or prompt_tokens < 0:
        raise ValueError("prompt_tokens must be a non-negative integer")
        
    if not isinstance(completion_tokens, int) or completion_tokens < 0:
        raise ValueError("completion_tokens must be a non-negative integer")
        
    if not isinstance(total_tokens, int) or total_tokens < 0:
        raise ValueError("total_tokens must be a non-negative integer")
        
    # Check token count consistency
    if total_tokens != prompt_tokens + completion_tokens:
        raise ValueError(f"total_tokens ({total_tokens}) must equal prompt_tokens ({prompt_tokens}) + completion_tokens ({completion_tokens})")
    
    # Check latency
    if latency_ms is not None and (not isinstance(latency_ms, (int, float)) or latency_ms < 0):
        raise ValueError("latency_ms must be a non-negative number")
        
    # Check endpoint name
    if endpoint_name is not None and not isinstance(endpoint_name, str):
        raise ValueError("endpoint_name must be a string")
        
def validate_messages(messages: Any) -> None:
    """
    Validate the messages format for LLM completion.
    
    Args:
        messages: List of message dictionaries
        
    Raises:
        ValueError: If messages format is invalid
    """
    if not isinstance(messages, list) or not messages:
        raise ValueError("Messages must be a non-empty list")
        
    for msg in messages:
        if not isinstance(msg, dict):
            raise ValueError("Each message must be a dictionary")
            
        if "role" not in msg or "content" not in msg:
            raise ValueError("Each message must contain 'role' and 'content' keys")
            
        if not isinstance(msg["role"], str) or not msg["role"]:
            raise ValueError("Message role must be a non-empty string")
            
        if not isinstance(msg["content"], str):
            # Some APIs allow None content, but generally it should be a string
            if msg["content"] is not None:
                raise ValueError("Message content must be a string or None") 