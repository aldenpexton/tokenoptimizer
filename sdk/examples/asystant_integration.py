"""
Example integration of TokenOptimizer SDK with asystant.ai
"""

import os
import sys
from typing import Dict, Any, List, Optional, Union

# Add the parent directory to sys.path to import the SDK
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the SDK
from tokenoptimizer import tracked_completion
from tokenoptimizer.utils import set_config

# Configuration - in production, set this to your actual TokenOptimizer backend URL
TOKENOPTIMIZER_API_URL = os.environ.get("TOKENOPTIMIZER_API_URL", "http://localhost:5000/api/log")

# Set the API URL to point to your TokenOptimizer backend
set_config(api_url=TOKENOPTIMIZER_API_URL)

class AsystantAI:
    """Mock asystant.ai framework with TokenOptimizer integration."""
    
    def __init__(self):
        """Initialize clients for each provider."""
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize clients for each supported LLM provider."""
        self.clients = {}
        
        # Initialize OpenAI if available
        if os.environ.get("OPENAI_API_KEY"):
            try:
                from openai import OpenAI
                self.clients["openai"] = OpenAI()
                print("✅ OpenAI client initialized")
            except ImportError:
                print("⚠️ OpenAI package not installed")
        
        # Initialize Anthropic if available
        if os.environ.get("ANTHROPIC_API_KEY"):
            try:
                import anthropic
                self.clients["anthropic"] = anthropic.Anthropic()
                print("✅ Anthropic client initialized")
            except ImportError:
                print("⚠️ Anthropic package not installed")
        
        # Initialize Gemini if available
        if os.environ.get("GOOGLE_API_KEY"):
            try:
                import google.generativeai as genai
                genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
                self.clients["gemini"] = genai
                print("✅ Gemini client initialized")
            except ImportError:
                print("⚠️ Google Generative AI package not installed")
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Return available models by provider."""
        models = {}
        
        if "openai" in self.clients:
            models["openai"] = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
        
        if "anthropic" in self.clients:
            models["anthropic"] = ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
        
        if "gemini" in self.clients:
            models["gemini"] = ["gemini-pro", "gemini-1.5-pro"]
        
        return models
    
    def detect_provider(self, model: str) -> str:
        """Detect which provider a model belongs to."""
        if model.startswith("gpt"):
            return "openai"
        elif model.startswith("claude"):
            return "anthropic"
        elif model.startswith("gemini"):
            return "gemini"
        else:
            raise ValueError(f"Unknown model provider for model: {model}")
    
    def generate_response(self, 
                          prompt: str, 
                          model: str, 
                          system_prompt: Optional[str] = None,
                          feature_name: str = "default") -> Dict[str, Any]:
        """
        Generate a response using the specified model with token tracking.
        
        Args:
            prompt: The user prompt
            model: The model to use
            system_prompt: Optional system prompt (for models that support it)
            feature_name: Name of the feature/endpoint using this call
            
        Returns:
            Dictionary with response text and metadata
        """
        provider = self.detect_provider(model)
        
        if provider not in self.clients:
            raise ValueError(f"Provider {provider} is not initialized")
        
        client = self.clients[provider]
        
        # Prepare messages format (compatible with all providers)
        messages = []
        if system_prompt and provider != "gemini":  # Gemini doesn't use system prompts
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Call the LLM with token tracking
        response = tracked_completion(
            model=model,
            messages=messages,
            endpoint_name=feature_name,  # Track which feature is making the call
            provider_client=client
        )
        
        # Extract response based on provider
        response_text = ""
        token_usage = {}
        
        if provider == "openai":
            response_text = response.choices[0].message.content
            token_usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        elif provider == "anthropic":
            response_text = response.content[0].text
            token_usage = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
        elif provider == "gemini":
            response_text = response.text
            # Gemini token usage is available through our adapter
            if hasattr(response, 'usage'):
                token_usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            else:
                token_usage = {"total_tokens": "Not available"}
        
        return {
            "text": response_text,
            "model": model,
            "provider": provider,
            "token_usage": token_usage
        }

def main():
    """Example usage of the asystant.ai integration."""
    asystant = AsystantAI()
    
    print("\nAvailable models:")
    for provider, models in asystant.get_available_models().items():
        for model in models:
            print(f"- {model} ({provider})")
    
    # Example prompts
    prompts = [
        "What are the benefits of token optimization for AI applications?",
        "Write a haiku about software efficiency.",
        "Explain the concept of API monitoring in one sentence."
    ]
    
    # Try with different models if available
    available_models = []
    for provider, models in asystant.get_available_models().items():
        if models:
            available_models.append(models[0])
    
    if not available_models:
        print("\nNo models available. Please set API keys for at least one provider.")
        return
    
    print("\nGenerating responses with token tracking:")
    for i, prompt in enumerate(prompts):
        if i >= len(available_models):
            break
            
        model = available_models[i]
        print(f"\n\nPrompt: {prompt}")
        print(f"Model: {model}")
        
        try:
            response = asystant.generate_response(
                prompt=prompt,
                model=model,
                system_prompt="You are a helpful assistant that gives concise answers.",
                feature_name=f"example_feature_{i+1}"
            )
            
            print(f"Response: {response['text']}")
            print(f"Token usage: {response['token_usage']}")
            print("TokenOptimizer has tracked this request.")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nAll token usage from these requests has been logged to TokenOptimizer.")
    print("Check your TokenOptimizer dashboard to see the data.")

if __name__ == "__main__":
    main() 