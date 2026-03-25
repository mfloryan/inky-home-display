from unittest.mock import patch, Mock
import weather

@patch("weather.load_token", return_value="fake-token")
@patch("weather.requests.get")
def test_get_weather_calls_requests_with_timeout(mock_get, mock_load_token):
    mock_response = Mock()
    mock_response.json.return_value = {
        "name": "Stockholm",
        "sys": {"sunrise": 1600000000, "sunset": 1600040000},
        "main": {"temp": 15},
        "weather": [{"description": "clear sky"}],
        "list": [
            {
                "dt": 1600000000,
                "main": {"temp": 15},
                "weather": [{"description": "clear sky"}]
            }
        ]
    }
    mock_get.return_value = mock_response

    weather.get_weather()

    assert mock_get.call_count == 2
    mock_get.assert_any_call("https://api.openweathermap.org/data/2.5/weather", params={
        "lat": "59.4308",
        "lon": "18.0637",
        "units": "metric",
        "lang": "pl",
        "appid": "fake-token",
    }, timeout=10)
    mock_get.assert_any_call("https://api.openweathermap.org/data/2.5/forecast", params={
        "lat": "59.4308",
        "lon": "18.0637",
        "units": "metric",
        "lang": "pl",
        "appid": "fake-token",
        "cnt": 8
    }, timeout=10)
