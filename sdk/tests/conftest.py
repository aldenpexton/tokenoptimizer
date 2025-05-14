"""
Pytest configuration and shared fixtures.
"""
import os
import json
import pytest
from unittest.mock import MagicMock, PropertyMock

# Set environment variables for testing
os.environ["TOKENOPTIMIZER_API_URL"] = "http://test-api.tokenoptimizer.com/api/log"
os.environ["TOKENOPTIMIZER_DEBUG"] = "true"

@pytest.fixture
def mock_requests_post(monkeypatch):
    """Mock the requests.post method for testing."""
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "message": "Token usage logged successfully",
        "log": {
            "model": "gpt-4",
            "prompt_tokens": 150,
            "completion_tokens": 50,
            "total_tokens": 200,
            "latency_ms": 1200,
            "endpoint_name": "test-endpoint",
            "timestamp": "2023-05-01T12:34:56Z",
            "input_cost": 0.0045,
            "output_cost": 0.003,
            "total_cost": 0.0075,
            "api_provider": "OpenAI"
        }
    }
    
    mock_post = MagicMock(return_value=mock_response)
    monkeypatch.setattr("requests.post", mock_post)
    return mock_post

@pytest.fixture
def openai_client_mock():
    """Create a mock for the OpenAI client."""
    client = MagicMock()
    
    # Mock structure for the new OpenAI client (>=1.0.0)
    chat_completions = MagicMock()
    client.chat = MagicMock()
    client.chat.completions = chat_completions
    
    # Create mock response
    mock_response = MagicMock()
    
    # Create a proper usage object with integer values
    usage = MagicMock()
    type(usage).prompt_tokens = PropertyMock(return_value=150)
    type(usage).completion_tokens = PropertyMock(return_value=50)
    type(usage).total_tokens = PropertyMock(return_value=200)
    
    # Attach usage to response
    type(mock_response).usage = PropertyMock(return_value=usage)
    
    # Create choice objects
    choice = MagicMock()
    message = MagicMock()
    type(message).content = PropertyMock(return_value="This is a test response")
    type(choice).message = PropertyMock(return_value=message)
    
    # Create choices list
    choices = [choice]
    type(mock_response).choices = PropertyMock(return_value=choices)
    
    # Setup the create method to return the mock response
    chat_completions.create = MagicMock(return_value=mock_response)
    
    return client

@pytest.fixture
def anthropic_client_mock():
    """Create a mock for the Anthropic client."""
    client = MagicMock()
    
    # Mock structure for the new Anthropic client
    messages = MagicMock()
    client.messages = messages
    
    # Create mock response
    mock_response = MagicMock()
    
    # Create a proper usage object with integer values
    usage = MagicMock()
    type(usage).input_tokens = PropertyMock(return_value=150)
    type(usage).output_tokens = PropertyMock(return_value=50)
    
    # Attach usage to response
    type(mock_response).usage = PropertyMock(return_value=usage)
    
    # Create content list with text
    content_item = MagicMock()
    type(content_item).text = PropertyMock(return_value="This is a test response")
    content = [content_item]
    type(mock_response).content = PropertyMock(return_value=content)
    
    # Setup the create method to return the mock response
    messages.create = MagicMock(return_value=mock_response)
    
    return client

@pytest.fixture
def mistral_client_mock():
    """Create a mock for the Mistral client."""
    client = MagicMock()
    
    # Mock structure for Mistral client
    chat_completions = MagicMock()
    client.chat = MagicMock()
    client.chat.completions = chat_completions
    
    # Create mock response
    mock_response = MagicMock()
    
    # Create a proper usage object with integer values
    usage = MagicMock()
    type(usage).prompt_tokens = PropertyMock(return_value=150)
    type(usage).completion_tokens = PropertyMock(return_value=50)
    type(usage).total_tokens = PropertyMock(return_value=200)
    
    # Attach usage to response
    type(mock_response).usage = PropertyMock(return_value=usage)
    
    # Create choice objects
    choice = MagicMock()
    message = MagicMock()
    type(message).content = PropertyMock(return_value="This is a test response")
    type(choice).message = PropertyMock(return_value=message)
    
    # Create choices list
    choices = [choice]
    type(mock_response).choices = PropertyMock(return_value=choices)
    
    # Setup the create method to return the mock response
    chat_completions.create = MagicMock(return_value=mock_response)
    
    return client 