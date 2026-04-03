import sys
from unittest.mock import Mock, patch, mock_open
import pytest

# Mock requests before importing weather
sys.modules["requests"] = Mock()
import weather

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

def test_get_weather_parse_forecast_logic():
    from datetime import datetime

    mock_weather_response = {
        "name": "Stockholm",
        "sys": {"sunrise": 1618290000, "sunset": 1618340000},
        "main": {"temp": 10.5},
        "weather": [{"description": "clear sky"}]
    }

    mock_forecast_response = {
        "list": [
            {
                "dt": 1618317200,
                "main": {"temp": 20.1},
                "weather": [{"description": "clear sky"}]
            },
            {
                "dt": 1618320800,
                "main": {"temp": 21.2},
                "weather": [{"description": "few clouds"}]
            }
        ]
    }

    with patch("weather.load_token", return_value="dummy_token"):
        # Setup mock return values for requests.get
        mock_get_weather = Mock()
        mock_get_weather.json.return_value = mock_weather_response

        mock_get_forecast = Mock()
        mock_get_forecast.json.return_value = mock_forecast_response

        sys.modules["requests"].get.side_effect = [
            mock_get_weather,
            mock_get_forecast
        ]

        result = weather.get_weather()

        assert result["name"] == "Stockholm"
        assert len(result["forecast"]) == 2
        assert result["forecast"][0]["temp"] == 20.1
        assert result["forecast"][0]["weather"] == "clear sky"
        assert isinstance(result["forecast"][0]["time"], datetime)
        assert result["forecast"][1]["temp"] == 21.2
        assert result["forecast"][1]["weather"] == "few clouds"
