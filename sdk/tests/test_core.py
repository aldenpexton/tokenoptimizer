"""
Tests for the core functionality of the TokenOptimizer SDK.
"""
import pytest
import time
from unittest.mock import patch, MagicMock

from tokenoptimizer.core import track_usage, tracked_completion

class TestTrackUsage:
    """Tests for the track_usage function."""
    
    def test_track_usage_success(self, mock_requests_post):
        """Test successful token usage tracking."""
        result = track_usage(
            model="gpt-4",
            prompt_tokens=150,
            completion_tokens=50,
            total_tokens=200,
            latency_ms=1200,
            endpoint_name="test-endpoint"
        )
        
        # Verify the request was made with the correct data
        mock_requests_post.assert_called_once()
        args, kwargs = mock_requests_post.call_args
        
        # Check URL
        assert kwargs["url"] == "http://test-api.tokenoptimizer.com/api/log"
        
        # Check payload
        payload = kwargs["json"]
        assert payload["model"] == "gpt-4"
        assert payload["prompt_tokens"] == 150
        assert payload["completion_tokens"] == 50
        assert payload["total_tokens"] == 200
        assert payload["latency_ms"] == 1200
        assert payload["endpoint_name"] == "test-endpoint"
        assert "timestamp" in payload
        assert "api_provider" in payload
        assert payload["api_provider"] == "OpenAI"  # Should be inferred from model name
        
        # Check result
        assert result["success"] is True
        assert "log" in result
        
    def test_track_usage_validation_error(self):
        """Test token usage tracking with invalid inputs."""
        with pytest.raises(ValueError):
            # total_tokens doesn't match sum of prompt and completion tokens
            track_usage(
                model="gpt-4",
                prompt_tokens=150,
                completion_tokens=50,
                total_tokens=250,  # Should be 200
                latency_ms=1200
            )
        
        with pytest.raises(ValueError):
            # Negative token count
            track_usage(
                model="gpt-4",
                prompt_tokens=-10,
                completion_tokens=50,
                total_tokens=40,
                latency_ms=1200
            )
            
        with pytest.raises(ValueError):
            # Empty model name
            track_usage(
                model="",
                prompt_tokens=150,
                completion_tokens=50,
                total_tokens=200,
                latency_ms=1200
            )
    
    def test_track_usage_api_error(self, monkeypatch):
        """Test token usage tracking with API error."""
        # Mock failed API response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post = MagicMock(return_value=mock_response)
        monkeypatch.setattr("requests.post", mock_post)
        
        result = track_usage(
            model="gpt-4",
            prompt_tokens=150,
            completion_tokens=50,
            total_tokens=200,
            latency_ms=1200
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "500" in result["error"]
        
    def test_track_usage_exception(self, monkeypatch):
        """Test token usage tracking with exception during API call."""
        # Mock exception during API call
        def mock_post_with_exception(*args, **kwargs):
            raise Exception("Connection error")
            
        monkeypatch.setattr("requests.post", mock_post_with_exception)
        
        result = track_usage(
            model="gpt-4",
            prompt_tokens=150,
            completion_tokens=50,
            total_tokens=200,
            latency_ms=1200
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "Connection error" in result["error"]
        

class TestTrackedCompletion:
    """Tests for the tracked_completion function."""
    
    def test_tracked_completion_with_openai(self, mock_requests_post, openai_client_mock):
        """Test tracked completion with OpenAI client."""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello"}
        ]
        
        with patch("time.time", side_effect=[100, 101.2]):  # Mock time for latency calculation
            response = tracked_completion(
                model="gpt-4",
                messages=messages,
                endpoint_name="test-chat",
                provider_client=openai_client_mock
            )
        
        # Verify the client was called correctly
        openai_client_mock.chat.completions.create.assert_called_once_with(
            model="gpt-4",
            messages=messages
        )
        
        # Verify the API request was made
        mock_requests_post.assert_called_once()
        
        # Check response
        assert response.choices[0].message.content == "This is a test response"
    
    def test_tracked_completion_with_anthropic(self, mock_requests_post, anthropic_client_mock):
        """Test tracked completion with Anthropic client."""
        messages = [
            {"role": "user", "content": "Hello"}
        ]
        
        with patch("time.time", side_effect=[100, 101.2]):  # Mock time for latency calculation
            response = tracked_completion(
                model="claude-3-haiku",
                messages=messages,
                endpoint_name="test-chat",
                provider_client=anthropic_client_mock
            )
        
        # Verify the client was called correctly
        anthropic_client_mock.messages.create.assert_called_once_with(
            model="claude-3-haiku",
            messages=messages
        )
        
        # Verify the API request was made
        mock_requests_post.assert_called_once()
        
        # Check response
        assert response.content[0].text == "This is a test response"
    
    def test_tracked_completion_with_mistral(self, mock_requests_post, mistral_client_mock):
        """Test tracked completion with Mistral client."""
        messages = [
            {"role": "user", "content": "Hello"}
        ]
        
        with patch("time.time", side_effect=[100, 101.2]):  # Mock time for latency calculation
            response = tracked_completion(
                model="mistral-medium",
                messages=messages,
                endpoint_name="test-chat",
                provider_client=mistral_client_mock
            )
        
        # Verify the client was called correctly
        mistral_client_mock.chat.completions.create.assert_called_once_with(
            model="mistral-medium",
            messages=messages
        )
        
        # Verify the API request was made
        mock_requests_post.assert_called_once()
        
        # Check response
        assert response.choices[0].message.content == "This is a test response"
    
    def test_tracked_completion_with_kwargs(self, mock_requests_post, openai_client_mock):
        """Test tracked completion with additional kwargs."""
        messages = [
            {"role": "user", "content": "Hello"}
        ]
        
        tracked_completion(
            model="gpt-4",
            messages=messages,
            endpoint_name="test-chat",
            provider_client=openai_client_mock,
            temperature=0.7,
            max_tokens=100
        )
        
        # Verify the additional kwargs were passed through
        openai_client_mock.chat.completions.create.assert_called_once_with(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=100
        )
    
    def test_tracked_completion_auto_detect_provider(self, mock_requests_post, monkeypatch):
        """Test auto-detection of provider based on model name."""
        # Mock the _detect_provider_from_model function
        mock_openai_client = MagicMock()
        
        with patch("tokenoptimizer.core._detect_provider_from_model",
                  return_value=mock_openai_client) as mock_detect:
            
            # Mock the adapter
            mock_adapter = MagicMock()
            mock_adapter.provider_name = "OpenAI"
            mock_adapter.complete.return_value = "test response"
            mock_adapter.extract_usage.return_value = {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
            
            with patch("tokenoptimizer.core.get_adapter", return_value=mock_adapter):
                tracked_completion(
                    model="gpt-4",
                    messages=[{"role": "user", "content": "Hello"}]
                )
            
            # Verify provider detection was called with correct model
            mock_detect.assert_called_once_with("gpt-4") 