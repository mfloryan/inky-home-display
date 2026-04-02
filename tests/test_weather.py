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
