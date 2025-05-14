"""
Base adapter interface for LLM providers.

This module defines the base adapter interface that all provider adapters must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class BaseAdapter(ABC):
    """
    Base adapter interface for LLM providers.
    
    This class defines the interface that all provider adapters must implement.
    """
    
    provider_name: str = "Unknown"
    
    def __init__(self, client: Any):
        """
        Initialize the adapter with a provider client.
        
        Args:
            client: The provider client instance
        """
        self.client = client
    
    @abstractmethod
    def complete(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Any:
        """
        Call the provider's completion API.
        
        Args:
            model: The model to use
            messages: List of message dictionaries
            **kwargs: Additional arguments to pass to the provider's API
            
        Returns:
            The provider's response
        """
        pass
    
    @abstractmethod
    def extract_usage(self, response: Any) -> Dict[str, int]:
        """
        Extract token usage information from the provider's response.
        
        Args:
            response: The provider's response
            
        Returns:
            Dict containing prompt_tokens, completion_tokens, and total_tokens
        """
        pass 