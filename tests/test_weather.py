import datetime
from unittest.mock import Mock, patch, mock_open
import pytest
import weather


@pytest.fixture
def mock_weather_response():
    mock_current = Mock()
    mock_current.json.return_value = {
        "name": "Stockholm",
        "sys": {"sunrise": 1600000000, "sunset": 1600040000},
        "main": {"temp": 5.2},
        "weather": [{"icon": "01d", "description": "clear sky"}],
    }
    mock_forecast = Mock()
    mock_forecast.json.return_value = {
        "list": [
            {
                "dt": 1600050000,
                "main": {"temp": 3.1},
                "weather": [{"icon": "02d", "description": "few clouds"}],
            }
        ]
    }
    return [mock_current, mock_forecast]


def test_load_token_returns_file_content_when_file_exists():
    weather.load_token.cache_clear()
    mock_file_content = "dummy_token_123"
    with patch("builtins.open", mock_open(read_data=mock_file_content)):
        token = weather.load_token()
        assert token == mock_file_content


def test_load_token_raises_error_when_file_not_found():
    weather.load_token.cache_clear()
    with patch("builtins.open", side_effect=FileNotFoundError()):
        with patch("tokens.logger") as mock_logger:
            with pytest.raises(RuntimeError, match="Unable to load Open Weather token"):
                weather.load_token()

            mock_logger.error.assert_called_once()


def test_get_weather_returns_structured_data(mock_weather_response):
    with patch("weather.load_token", return_value="test_token"):
        with patch("weather.requests.get", side_effect=mock_weather_response):
            result = weather.get_weather()

    assert result["name"] == "Stockholm"
    assert isinstance(result["sunrise"], datetime.datetime)
    assert isinstance(result["sunset"], datetime.datetime)
    assert result["now"]["temp"] == 5.2
    assert result["now"]["icon"] == "01d"
    assert len(result["forecast"]) == 1
    assert result["forecast"][0]["temp"] == 3.1
    assert result["forecast"][0]["icon"] == "02d"
    assert isinstance(result["forecast"][0]["time"], datetime.datetime)


def test_get_weather_uses_correct_params():
    with patch("weather.load_token", return_value="test_token"):
        with patch("weather.requests.get") as mock_get:
            mock_get.return_value.json.return_value = {
                "name": "S",
                "sys": {"sunrise": 0, "sunset": 0},
                "main": {"temp": 0},
                "weather": [{"icon": "i"}],
                "list": [],
            }
            weather.get_weather()

            # Check first call (current weather)
            args, kwargs = mock_get.call_args_list[0]
            assert "weather" in args[0]
            assert kwargs["params"]["appid"] == "test_token"
            assert kwargs["params"]["units"] == "metric"

            # Check second call (forecast)
            args, kwargs = mock_get.call_args_list[1]
            assert "forecast" in args[0]
            assert kwargs["params"]["cnt"] == 8
