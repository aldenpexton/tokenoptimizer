"""
Configuration handling for the TokenOptimizer SDK.

This module provides functions to get and set the SDK configuration.
"""

import os
import json
from typing import Dict, Any, Optional

# Default configuration
_DEFAULT_CONFIG = {
    "api_url": "http://localhost:5002/api/log",
    "timeout": 3,
    "debug": False,
    "disable_logging": False
}

# Current configuration
_config = _DEFAULT_CONFIG.copy()

# Try to load configuration from environment variables
if os.environ.get("TOKENOPTIMIZER_API_URL"):
    _config["api_url"] = os.environ.get("TOKENOPTIMIZER_API_URL")

if os.environ.get("TOKENOPTIMIZER_DEBUG"):
    _config["debug"] = os.environ.get("TOKENOPTIMIZER_DEBUG").lower() in ("true", "1", "yes")

def get_config() -> Dict[str, Any]:
    """
    Get the current SDK configuration.
    
    Returns:
        Dict containing the configuration settings
    """
    return _config.copy()

def set_config(
    api_url: Optional[str] = None,
    timeout: Optional[int] = None,
    debug: Optional[bool] = None,
    disable_logging: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Update the SDK configuration.
    
    Args:
        api_url: URL of the TokenOptimizer API
        timeout: Request timeout in seconds
        debug: Enable debug mode
        disable_logging: Disable all logging
        
    Returns:
        Dict containing the updated configuration
    """
    global _config
    
    if api_url is not None:
        _config["api_url"] = api_url
        
    if timeout is not None:
        _config["timeout"] = timeout
        
    if debug is not None:
        _config["debug"] = debug
        
    if disable_logging is not None:
        _config["disable_logging"] = disable_logging
        
    return get_config()

def reset_config() -> Dict[str, Any]:
    """
    Reset the configuration to default values.
    
    Returns:
        Dict containing the default configuration
    """
    global _config
    _config = _DEFAULT_CONFIG.copy()
    return get_config() 