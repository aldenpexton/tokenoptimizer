"""
TokenOptimizer SDK - Track and optimize your LLM API usage

This SDK provides a simple way to track token usage, latency, and costs
for LLM API calls to OpenAI, Anthropic, and other providers.
"""

from .core import tracked_completion, track_usage

__all__ = ['tracked_completion', 'track_usage']
__version__ = '0.1.0' 