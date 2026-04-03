import sys
from unittest.mock import Mock, patch
import weather

sys.modules["requests"] = Mock()

def test_get_weather_calls_load_token():
    with patch("weather.load_token") as mock_load_token:
        mock_load_token.return_value = "dummy_token"
        with patch("weather.requests.get") as mock_get:
            mock_get.return_value.json.return_value = {
                "name": "Test City",
                "sys": {"sunrise": 1600000000, "sunset": 1600040000},
                "main": {"temp": 20},
                "list": []
            }
            weather.get_weather()
            mock_load_token.assert_called_once_with("openweather-api-token", "Open Weather")
