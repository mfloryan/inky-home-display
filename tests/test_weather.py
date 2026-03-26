import sys
from unittest.mock import Mock, patch, mock_open
import pytest
import logging

sys.modules["requests"] = Mock()
import weather

@pytest.fixture(autouse=True)
def clear_weather_cache():
    weather.load_token.cache_clear()

def test_load_token_returns_file_content_when_file_exists():
    mock_file_content = "dummy_token_123"
    with patch("builtins.open", mock_open(read_data=mock_file_content)):
        token = weather.load_token()
        assert token == mock_file_content

def test_load_token_raises_error_when_file_not_found():
    with patch("builtins.open", side_effect=FileNotFoundError()):
        with patch("weather.logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            with pytest.raises(RuntimeError, match="Unable to load Open Weather token"):
                weather.load_token()

            mock_logger.error.assert_called_once_with("Token file `openweather-api-token` not found")
