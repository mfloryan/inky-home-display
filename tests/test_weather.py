import sys
from unittest.mock import Mock, patch, mock_open
import pytest
import weather

sys.modules["requests"] = Mock()

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


def _make_get_responses(current_icon="01d", forecast_icon="02d"):
    mock_current = Mock()
    mock_current.json.return_value = {
        "name": "Stockholm",
        "sys": {"sunrise": 1000000, "sunset": 1000100},
        "main": {"temp": 5.0},
        "weather": [{"icon": current_icon, "description": "clear sky"}],
    }
    mock_forecast_resp = Mock()
    mock_forecast_resp.json.return_value = {
        "list": [
            {
                "dt": 1000200,
                "main": {"temp": 3.0},
                "weather": [{"icon": forecast_icon, "description": "few clouds"}],
            }
        ]
    }
    return [mock_current, mock_forecast_resp]


def test_get_weather_includes_icon_in_current_conditions():
    with patch("weather.load_token", return_value="test_token"):
        with patch("weather.requests.get", side_effect=_make_get_responses(current_icon="01d")):
            result = weather.get_weather()
    assert result["now"]["icon"] == "01d"


def test_get_weather_includes_icon_in_forecast_items():
    with patch("weather.load_token", return_value="test_token"):
        with patch("weather.requests.get", side_effect=_make_get_responses(forecast_icon="02d")):
            result = weather.get_weather()
    assert result["forecast"][0]["icon"] == "02d"
