"""
Tests for utility functions in the TokenOptimizer SDK.
"""
import os
import pytest
from unittest.mock import patch

from tokenoptimizer.utils.config import get_config, set_config, reset_config
from tokenoptimizer.utils.validation import validate_input, validate_messages

class TestConfig:
    """Tests for the configuration utilities."""
    
    def test_get_config(self):
        """Test getting the configuration."""
        config = get_config()
        
        # Check that config is populated with values from environment variables
        assert config["api_url"] == "http://test-api.tokenoptimizer.com/api/log"
        assert config["debug"] is True
        
        # These should have default values
        assert config["timeout"] == 3
        assert config["disable_logging"] is False
    
    def test_set_config(self):
        """Test setting configuration values."""
        # Save original config
        original_config = get_config()
        
        try:
            # Update config
            updated_config = set_config(
                api_url="https://new-api.tokenoptimizer.com/api/log",
                timeout=10,
                debug=False,
                disable_logging=True
            )
            
            # Check returned config
            assert updated_config["api_url"] == "https://new-api.tokenoptimizer.com/api/log"
            assert updated_config["timeout"] == 10
            assert updated_config["debug"] is False
            assert updated_config["disable_logging"] is True
            
            # Check that get_config returns the updated values
            config = get_config()
            assert config["api_url"] == "https://new-api.tokenoptimizer.com/api/log"
            assert config["timeout"] == 10
            assert config["debug"] is False
            assert config["disable_logging"] is True
        finally:
            # Reset config to original values
            for key, value in original_config.items():
                set_config(**{key: value})
    
    def test_set_config_partial(self):
        """Test partial configuration updates."""
        # Save original config
        original_config = get_config()
        
        try:
            # Only update some values
            updated_config = set_config(
                api_url="https://partial-update.tokenoptimizer.com/api/log",
                debug=False
            )
            
            # Check returned config
            assert updated_config["api_url"] == "https://partial-update.tokenoptimizer.com/api/log"
            assert updated_config["debug"] is False
            
            # Other values should remain unchanged
            assert updated_config["timeout"] == original_config["timeout"]
            assert updated_config["disable_logging"] == original_config["disable_logging"]
        finally:
            # Reset config to original values
            for key, value in original_config.items():
                set_config(**{key: value})
    
    def test_reset_config(self):
        """Test resetting the configuration to defaults."""
        # Update config
        set_config(
            api_url="https://temp.tokenoptimizer.com/api/log",
            timeout=15,
            debug=False,
            disable_logging=True
        )
        
        # Reset config
        reset_config()
        
        # Check that config is reset to default values
        config = get_config()
        
        # Should be reset to default even though env var is set
        assert config["api_url"] == "http://localhost:5000/api/log"
        assert config["timeout"] == 3
        assert config["debug"] is False
        assert config["disable_logging"] is False
        
        # Restore environment-based config for other tests
        set_config(
            api_url=os.environ.get("TOKENOPTIMIZER_API_URL"),
            debug=os.environ.get("TOKENOPTIMIZER_DEBUG", "").lower() in ("true", "1", "yes")
        )


class TestValidation:
    """Tests for the validation utilities."""
    
    def test_validate_input_success(self):
        """Test successful input validation."""
        # Should not raise an exception
        validate_input(
            model="gpt-4",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150
        )
    
    def test_validate_input_model(self):
        """Test model name validation."""
        with pytest.raises(ValueError, match="Model name must be a non-empty string"):
            validate_input(
                model="",
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150
            )
            
        with pytest.raises(ValueError, match="Model name must be a non-empty string"):
            validate_input(
                model=None,
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150
            )
    
    def test_validate_input_token_counts(self):
        """Test token count validation."""
        with pytest.raises(ValueError, match="prompt_tokens must be a non-negative integer"):
            validate_input(
                model="gpt-4",
                prompt_tokens=-10,
                completion_tokens=50,
                total_tokens=40
            )
            
        with pytest.raises(ValueError, match="completion_tokens must be a non-negative integer"):
            validate_input(
                model="gpt-4",
                prompt_tokens=100,
                completion_tokens=-50,
                total_tokens=50
            )
            
        with pytest.raises(ValueError, match="total_tokens must be a non-negative integer"):
            validate_input(
                model="gpt-4",
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=-150
            )
    
    def test_validate_input_token_consistency(self):
        """Test token count consistency validation."""
        with pytest.raises(ValueError, match=r"total_tokens \(\d+\) must equal prompt_tokens \(\d+\) \+ completion_tokens \(\d+\)"):
            validate_input(
                model="gpt-4",
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=200  # Should be 150
            )
    
    def test_validate_input_latency(self):
        """Test latency validation."""
        with pytest.raises(ValueError, match="latency_ms must be a non-negative number"):
            validate_input(
                model="gpt-4",
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
                latency_ms=-100
            )
    
    def test_validate_input_endpoint_name(self):
        """Test endpoint name validation."""
        with pytest.raises(ValueError, match="endpoint_name must be a string"):
            validate_input(
                model="gpt-4",
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
                endpoint_name=123  # Should be a string
            )
    
    def test_validate_messages_success(self):
        """Test successful messages validation."""
        # Should not raise an exception
        validate_messages([
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello"}
        ])
    
    def test_validate_messages_empty(self):
        """Test empty messages validation."""
        with pytest.raises(ValueError, match="Messages must be a non-empty list"):
            validate_messages([])
            
        with pytest.raises(ValueError, match="Messages must be a non-empty list"):
            validate_messages(None)
            
        with pytest.raises(ValueError, match="Messages must be a non-empty list"):
            validate_messages("not a list")
    
    def test_validate_messages_format(self):
        """Test message format validation."""
        with pytest.raises(ValueError, match="Each message must be a dictionary"):
            validate_messages([
                {"role": "user", "content": "Hello"},
                "not a dictionary"
            ])
            
        with pytest.raises(ValueError, match="Each message must contain 'role' and 'content' keys"):
            validate_messages([
                {"role": "user", "content": "Hello"},
                {"text": "missing required keys"}
            ])
            
        with pytest.raises(ValueError, match="Message role must be a non-empty string"):
            validate_messages([
                {"role": "", "content": "Empty role"}
            ])
            
        with pytest.raises(ValueError, match="Message content must be a string or None"):
            validate_messages([
                {"role": "user", "content": 123}  # Should be a string
            ]) 