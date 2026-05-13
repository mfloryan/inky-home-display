import datetime
import sys
from unittest.mock import Mock, patch, mock_open
import pytest

mock_requests = Mock()

class MockRequestException(Exception):
    pass

class MockJSONDecodeError(Exception):
    pass

class MockHTTPError(MockRequestException):
    pass

class MockTimeout(MockRequestException):
    pass

mock_requests.exceptions.RequestException = MockRequestException
mock_requests.exceptions.JSONDecodeError = MockJSONDecodeError
mock_requests.exceptions.HTTPError = MockHTTPError
mock_requests.exceptions.Timeout = MockTimeout

sys.modules["requests"] = mock_requests

import weather  # noqa: E402

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


@patch("weather.requests.get")
def test_fetch_from_api_success(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {"key": "value"}
    mock_get.return_value = mock_response

    result = weather._fetch_from_api("http://test.url", {"param": "val"})

    mock_get.assert_called_once_with("http://test.url", params={"param": "val"}, timeout=10)
    mock_response.raise_for_status.assert_called_once()
    assert result == {"key": "value"}


@patch("weather.requests.get")
@patch("weather.logging.getLogger")
def test_fetch_from_api_json_decode_error(mock_get_logger, mock_get):
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_get.side_effect = weather.requests.exceptions.JSONDecodeError("mock error", "mock doc", 0)

    with pytest.raises(RuntimeError, match="Invalid JSON response"):
        weather._fetch_from_api("http://test.url", {})

    mock_logger.error.assert_called_once_with("Malformed JSON response from OpenWeather API")


@patch("weather.requests.get")
@patch("weather.logging.getLogger")
def test_fetch_from_api_request_exception(mock_get_logger, mock_get):
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_get.side_effect = weather.requests.exceptions.RequestException()

    with pytest.raises(RuntimeError, match="API request failed"):
        weather._fetch_from_api("http://test.url", {})

    mock_logger.error.assert_called_once_with("Error fetching data from OpenWeather API")


def test_get_weather_returns_structured_data(mock_weather_response):
    with patch("weather.load_token", return_value="test_token"):
        with patch("weather._fetch_from_api", side_effect=[r.json() for r in mock_weather_response]):
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
        with patch("weather._fetch_from_api") as mock_fetch:
            mock_fetch.side_effect = [
                {
                    "name": "S",
                    "sys": {"sunrise": 0, "sunset": 0},
                    "main": {"temp": 0},
                    "weather": [{"icon": "i"}],
                },
                {
                    "list": [],
                }
            ]
            weather.get_weather()

            # Check first call (current weather)
            args, kwargs = mock_fetch.call_args_list[0]
            assert "weather" in args[0]
            assert kwargs["params"]["appid"] == "test_token"
            assert kwargs["params"]["units"] == "metric"

            # Check second call (forecast)
            args, kwargs = mock_fetch.call_args_list[1]
            assert "forecast" in args[0]
            assert kwargs["params"]["cnt"] == 8
