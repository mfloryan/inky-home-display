import pytest
from unittest.mock import patch, mock_open, Mock
from config import load_token

def test_load_token_returns_file_content_when_file_exists():
    mock_file_content = "dummy_token_123"
    with patch("builtins.open", mock_open(read_data=mock_file_content)):
        token = load_token("test-token", "Test Service")
        assert token == mock_file_content

def test_load_token_raises_error_when_file_not_found():
    with patch("builtins.open", side_effect=FileNotFoundError()):
        with patch("config.logger") as mock_logger:
            with pytest.raises(RuntimeError, match="Unable to load Test Service token"):
                load_token("test-token", "Test Service")

            mock_logger.error.assert_called_once_with("Token file `%s` not found", "test-token")
