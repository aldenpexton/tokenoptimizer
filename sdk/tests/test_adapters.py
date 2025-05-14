"""
Tests for the adapters in the TokenOptimizer SDK.
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock

from tokenoptimizer.adapters import get_adapter
from tokenoptimizer.adapters.base_adapter import BaseAdapter
from tokenoptimizer.adapters.openai_adapter import OpenAIAdapter
from tokenoptimizer.adapters.anthropic_adapter import AnthropicAdapter
from tokenoptimizer.adapters.mistral_adapter import MistralAdapter
from tokenoptimizer.adapters.gemini_adapter import GeminiAdapter

class TestAdapterFactory:
    """Tests for the adapter factory function."""
    
    def test_get_adapter_openai_by_model(self):
        """Test getting an OpenAI adapter by model name."""
        client = MagicMock()
        adapter = get_adapter("gpt-4", client)
        
        assert isinstance(adapter, OpenAIAdapter)
        assert adapter.client is client
    
    def test_get_adapter_anthropic_by_model(self):
        """Test getting an Anthropic adapter by model name."""
        client = MagicMock()
        adapter = get_adapter("claude-3-opus", client)
        
        assert isinstance(adapter, AnthropicAdapter)
        assert adapter.client is client
    
    def test_get_adapter_mistral_by_model(self):
        """Test getting a Mistral adapter by model name."""
        client = MagicMock()
        adapter = get_adapter("mistral-medium", client)
        
        assert isinstance(adapter, MistralAdapter)
        assert adapter.client is client
    
    def test_get_adapter_gemini_by_model(self):
        """Test getting a Gemini adapter by model name."""
        client = MagicMock()
        adapter = get_adapter("gemini-1.5-pro", client)
        
        assert isinstance(adapter, GeminiAdapter)
        assert adapter.client is client
    
    def test_get_adapter_openai_by_client(self):
        """Test getting an OpenAI adapter based on client module."""
        client = MagicMock()
        client.__class__.__module__ = "openai.api_resources"
        
        adapter = get_adapter("custom-model", client)
        
        assert isinstance(adapter, OpenAIAdapter)
        assert adapter.client is client
    
    def test_get_adapter_anthropic_by_client(self):
        """Test getting an Anthropic adapter based on client module."""
        client = MagicMock()
        client.__class__.__module__ = "anthropic.resources"
        
        adapter = get_adapter("custom-model", client)
        
        assert isinstance(adapter, AnthropicAdapter)
        assert adapter.client is client
    
    def test_get_adapter_mistral_by_client(self):
        """Test getting a Mistral adapter based on client module."""
        client = MagicMock()
        client.__class__.__module__ = "mistralai.client"
        
        adapter = get_adapter("custom-model", client)
        
        assert isinstance(adapter, MistralAdapter)
        assert adapter.client is client
    
    def test_get_adapter_gemini_by_client(self):
        """Test getting a Gemini adapter based on client module."""
        client = MagicMock()
        client.__class__.__module__ = "google.generativeai"
        
        adapter = get_adapter("custom-model", client)
        
        assert isinstance(adapter, GeminiAdapter)
        assert adapter.client is client
    
    def test_get_adapter_unknown(self):
        """Test getting an adapter for an unknown model/client."""
        client = MagicMock()
        client.__class__.__module__ = "unknown.client"
        
        with pytest.raises(ValueError, match="No adapter found for model"):
            get_adapter("unknown-model", client)


class TestOpenAIAdapter:
    """Tests for the OpenAI adapter."""
    
    def test_complete_new_api(self):
        """Test completion with the new OpenAI API."""
        # Mock the OpenAI client
        client = MagicMock()
        client.chat.completions.create.return_value = "test response"
        
        adapter = OpenAIAdapter(client)
        result = adapter.complete(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.7
        )
        
        # Verify the client was called correctly
        client.chat.completions.create.assert_called_once_with(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.7
        )
        
        assert result == "test response"
    
    def test_complete_legacy_api(self):
        """Test completion with the legacy OpenAI API."""
        # Mock the legacy OpenAI client
        client = MagicMock()
        
        # Setup the client to not have the new API
        type(client).chat = PropertyMock(return_value=None)
        
        client.ChatCompletion.create.return_value = "test response"
        
        adapter = OpenAIAdapter(client)
        result = adapter.complete(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.7
        )
        
        # Verify the client was called correctly
        client.ChatCompletion.create.assert_called_once_with(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.7
        )
        
        assert result == "test response"
    
    def test_complete_unsupported_client(self):
        """Test completion with an unsupported client format."""
        client = MagicMock()
        # Ensure client has no acceptable APIs
        type(client).chat = PropertyMock(return_value=None)
        type(client).ChatCompletion = PropertyMock(return_value=None)
        
        adapter = OpenAIAdapter(client)
        with pytest.raises(ValueError, match="Unsupported OpenAI client format"):
            adapter.complete(
                model="gpt-4",
                messages=[{"role": "user", "content": "Hello"}]
            )
    
    def test_extract_usage_new_api(self):
        """Test extracting usage info from new API response."""
        # Mock response object
        response = MagicMock()
        response.usage.prompt_tokens = 150
        response.usage.completion_tokens = 50
        response.usage.total_tokens = 200
        
        adapter = OpenAIAdapter(MagicMock())
        usage = adapter.extract_usage(response)
        
        assert usage["prompt_tokens"] == 150
        assert usage["completion_tokens"] == 50
        assert usage["total_tokens"] == 200
    
    def test_extract_usage_legacy_api(self):
        """Test extracting usage info from legacy API response."""
        # Mock response dict
        response = {
            "usage": {
                "prompt_tokens": 150,
                "completion_tokens": 50,
                "total_tokens": 200
            }
        }
        
        adapter = OpenAIAdapter(MagicMock())
        usage = adapter.extract_usage(response)
        
        assert usage["prompt_tokens"] == 150
        assert usage["completion_tokens"] == 50
        assert usage["total_tokens"] == 200
    
    def test_extract_usage_error(self):
        """Test error handling when extracting usage info."""
        # Response without usage info
        response = {"choices": []}
        
        adapter = OpenAIAdapter(MagicMock())
        
        # Using a try block instead of pytest.raises to handle the error directly
        try:
            adapter.extract_usage(response)
            # Should not reach here
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Could not extract token usage" in str(e)


class TestAnthropicAdapter:
    """Tests for the Anthropic adapter."""
    
    def test_complete_new_api(self):
        """Test completion with the new Anthropic API."""
        # Mock the Anthropic client
        client = MagicMock()
        client.messages.create.return_value = "test response"
        
        adapter = AnthropicAdapter(client)
        result = adapter.complete(
            model="claude-3-haiku",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=100
        )
        
        # Verify the client was called correctly
        client.messages.create.assert_called_once_with(
            model="claude-3-haiku",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=100
        )
        
        assert result == "test response"
    
    def test_extract_usage_new_api(self):
        """Test extracting usage info from new API response."""
        # Mock response object
        response = MagicMock()
        response.usage.input_tokens = 150
        response.usage.output_tokens = 50
        
        adapter = AnthropicAdapter(MagicMock())
        usage = adapter.extract_usage(response)
        
        assert usage["prompt_tokens"] == 150
        assert usage["completion_tokens"] == 50
        assert usage["total_tokens"] == 200
    
    def test_extract_usage_dict(self):
        """Test extracting usage info from response dict."""
        # Mock response dict
        response = {
            "usage": {
                "input_tokens": 150,
                "output_tokens": 50
            }
        }
        
        adapter = AnthropicAdapter(MagicMock())
        usage = adapter.extract_usage(response)
        
        assert usage["prompt_tokens"] == 150
        assert usage["completion_tokens"] == 50
        assert usage["total_tokens"] == 200
    
    def test_extract_usage_fallback(self):
        """Test fallback estimation when usage info is missing."""
        # Mock response with content but no usage
        response = MagicMock()
        
        # Set content to a string value with PropertyMock
        text_content = "This is a test response with approximately 10 tokens"
        type(response).content = PropertyMock(return_value=text_content)
        
        # Ensure there's no usage attribute
        type(response).usage = PropertyMock(side_effect=AttributeError("No usage attribute"))
        
        adapter = AnthropicAdapter(MagicMock())
        usage = adapter.extract_usage(response)
        
        # Should estimate based on content
        assert isinstance(usage["completion_tokens"], int)
        assert usage["completion_tokens"] > 0
        assert usage["total_tokens"] == usage["completion_tokens"]


class TestMistralAdapter:
    """Tests for the Mistral adapter."""
    
    def test_complete_direct_chat(self):
        """Test completion with the direct chat method."""
        # Mock the Mistral client
        client = MagicMock()
        client.chat = MagicMock(return_value="test response")
        
        adapter = MistralAdapter(client)
        result = adapter.complete(
            model="mistral-medium",
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.7
        )
        
        # Verify the client was called correctly
        client.chat.assert_called_once_with(
            model="mistral-medium",
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.7
        )
        
        assert result == "test response"
    
    def test_complete_openai_like(self):
        """Test completion with an OpenAI-like structure."""
        # Mock the Mistral client with OpenAI-like structure
        client = MagicMock()
        # Make sure chat is not callable
        client.chat = MagicMock(spec=[])  # Empty spec ensures it's not callable
        # Add completions.create method
        client.chat.completions = MagicMock()
        client.chat.completions.create = MagicMock(return_value="test response")
        
        adapter = MistralAdapter(client)
        result = adapter.complete(
            model="mistral-medium",
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.7
        )
        
        # Verify the client was called correctly
        client.chat.completions.create.assert_called_once_with(
            model="mistral-medium",
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.7
        )
        
        assert result == "test response"
    
    def test_complete_unsupported_client(self):
        """Test completion with an unsupported client format."""
        client = MagicMock()
        # Ensure client has no acceptable APIs
        type(client).chat = PropertyMock(return_value=None)
        
        adapter = MistralAdapter(client)
        with pytest.raises(ValueError, match="Unsupported Mistral AI client format"):
            adapter.complete(
                model="mistral-medium",
                messages=[{"role": "user", "content": "Hello"}]
            )
    
    def test_extract_usage_with_usage(self):
        """Test extracting usage info from response with usage field."""
        # Mock response object with real integer values
        response = MagicMock()
        
        # Create a proper usage object with integer values
        usage = MagicMock()
        type(usage).prompt_tokens = PropertyMock(return_value=150)
        type(usage).completion_tokens = PropertyMock(return_value=50)
        type(usage).total_tokens = PropertyMock(return_value=200)
        
        # Attach usage to response
        type(response).usage = PropertyMock(return_value=usage)
        
        adapter = MistralAdapter(MagicMock())
        result_usage = adapter.extract_usage(response)
        
        assert result_usage["prompt_tokens"] == 150
        assert result_usage["completion_tokens"] == 50
        assert result_usage["total_tokens"] == 200
    
    def test_extract_usage_alternative_names(self):
        """Test extracting usage with alternative field names."""
        # Mock response object with alternative field names
        response = MagicMock()
        response.usage.input_tokens = 150
        response.usage.output_tokens = 50
        response.usage.total_tokens = 200
        
        adapter = MistralAdapter(MagicMock())
        usage = adapter.extract_usage(response)
        
        assert usage["prompt_tokens"] == 150
        assert usage["completion_tokens"] == 50
        assert usage["total_tokens"] == 200
    
    def test_extract_usage_fallback(self):
        """Test fallback estimation when usage info is missing."""
        # Mock response with content but no usage
        response = MagicMock()
        
        # Create choice objects with content
        choice = MagicMock()
        message = MagicMock()
        type(message).content = PropertyMock(return_value="This is a test response with approximately 10 tokens")
        type(choice).message = PropertyMock(return_value=message)
        
        # Create choices list
        choices = [choice]
        type(response).choices = PropertyMock(return_value=choices)
        
        # Ensure response has no usage attribute
        type(response).usage = PropertyMock(side_effect=AttributeError("No usage attribute"))
        
        adapter = MistralAdapter(MagicMock())
        usage = adapter.extract_usage(response)
        
        # Should estimate based on content
        assert isinstance(usage["completion_tokens"], int)
        assert usage["completion_tokens"] > 0
        assert usage["total_tokens"] == usage["completion_tokens"]


class TestGeminiAdapter:
    """Tests for the Gemini adapter."""
    
    def test_complete_generate_content(self):
        """Test completion with the generate_content method."""
        # Mock the Gemini client
        client = MagicMock()
        client.generate_content.return_value = "test response"
        
        adapter = GeminiAdapter(client)
        result = adapter.complete(
            model="gemini-1.5-pro",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Hello"}
            ]
        )
        
        # Verify message transformation and client call
        client.generate_content.assert_called_once()
        called_messages = client.generate_content.call_args[0][0]
        
        # Check proper message conversion
        assert len(called_messages) == 2
        assert called_messages[0]["role"] == "user"
        assert called_messages[0]["parts"][0]["text"] == "You are a helpful assistant"
        assert called_messages[1]["role"] == "user"
        assert called_messages[1]["parts"][0]["text"] == "Hello"
        
        assert result == "test response"
    
    def test_complete_chat_method(self):
        """Test completion with the chat method."""
        # Mock the Gemini client without generate_content
        client = MagicMock()
        # No generate_content attribute
        delattr(client, "generate_content") if hasattr(client, "generate_content") else None
        # Add chat method
        client.chat = MagicMock(return_value="test response")
        
        adapter = GeminiAdapter(client)
        result = adapter.complete(
            model="gemini-1.5-pro",
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.7
        )
        
        # Verify the client was called correctly
        client.chat.assert_called_once_with(
            model="gemini-1.5-pro",
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.7
        )
        
        assert result == "test response"
    
    def test_complete_unsupported_client(self):
        """Test completion with an unsupported client format."""
        # Mock client with neither generate_content nor chat methods
        client = MagicMock()
        delattr(client, "generate_content") if hasattr(client, "generate_content") else None
        delattr(client, "chat") if hasattr(client, "chat") else None
        
        adapter = GeminiAdapter(client)
        with pytest.raises(ValueError, match="Unsupported Google Gemini client format"):
            adapter.complete(
                model="gemini-1.5-pro",
                messages=[{"role": "user", "content": "Hello"}]
            )
    
    def test_extract_usage_metadata(self):
        """Test extracting usage from usage_metadata field."""
        # Mock response with usage_metadata
        response = MagicMock()
        usage_metadata = MagicMock()
        usage_metadata.prompt_token_count = 150
        usage_metadata.candidates_token_count = 50
        response.usage_metadata = usage_metadata
        
        adapter = GeminiAdapter(MagicMock())
        usage = adapter.extract_usage(response)
        
        assert usage["prompt_tokens"] == 150
        assert usage["completion_tokens"] == 50
        assert usage["total_tokens"] == 200
    
    def test_extract_usage_dict_format(self):
        """Test extracting usage from dictionary format."""
        # Mock response dict
        response = {
            "usage_metadata": {
                "prompt_token_count": 150,
                "candidates_token_count": 50
            }
        }
        
        adapter = GeminiAdapter(MagicMock())
        usage = adapter.extract_usage(response)
        
        assert usage["prompt_tokens"] == 150
        assert usage["completion_tokens"] == 50
        assert usage["total_tokens"] == 200
    
    def test_extract_usage_fallback(self):
        """Test fallback handling when token data is missing."""
        # Create a dictionary instead of a MagicMock to avoid auto-creation of attributes
        response = {}
        
        adapter = GeminiAdapter(MagicMock())
        usage = adapter.extract_usage(response)
        
        # Should fall back to zeros
        assert usage["prompt_tokens"] == 0
        assert usage["completion_tokens"] == 0
        assert usage["total_tokens"] == 0 