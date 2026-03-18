from datetime import datetime
from unittest.mock import Mock, patch
import pytest

import tibber


def test_load_token_raises_error_when_file_not_found():
    with patch("builtins.open") as mock_open:
        mock_open.side_effect = FileNotFoundError()
        with pytest.raises(RuntimeError, match="Unable to load Tibber token"):
            tibber.load_token()


@patch("tibber.load_token")
def test_load_prices_raises_error_when_no_homes_in_response(mock_load_token):
    mock_load_token.return_value = "dummy_token"
    with patch("tibber.load_data_from_tibber") as mock_load:
        mock_load.return_value = {"data": {"viewer": {"homes": []}}}

        with pytest.raises(
            RuntimeError, match="No homes found in Tibber API response"
        ):
            tibber.load_prices_from_tibber()


@patch("tibber.load_token")
def test_load_prices_raises_error_when_current_subscription_is_none(mock_load_token):
    mock_load_token.return_value = "dummy_token"
    with patch("tibber.load_data_from_tibber") as mock_load:
        mock_load.return_value = {
            "data": {"viewer": {"homes": [{"currentSubscription": None}]}}
        }

        with pytest.raises(
            RuntimeError,
            match="No active subscription found in Tibber API response",
        ):
            tibber.load_prices_from_tibber()


@patch("tibber.load_token")
def test_load_prices_raises_error_when_price_info_is_none(mock_load_token):
    mock_load_token.return_value = "dummy_token"
    with patch("tibber.load_data_from_tibber") as mock_load:
        mock_load.return_value = {
            "data": {
                "viewer": {"homes": [{"currentSubscription": {"priceInfo": None}}]}
            }
        }

        with pytest.raises(
            RuntimeError,
            match="No price information available in Tibber API response",
        ):
            tibber.load_prices_from_tibber()


@patch("tibber.load_token")
def test_load_prices_raises_error_when_today_prices_is_none(mock_load_token):
    mock_load_token.return_value = "dummy_token"
    with patch("tibber.load_data_from_tibber") as mock_load:
        mock_load.return_value = {
            "data": {
                "viewer": {
                    "homes": [{"currentSubscription": {"priceInfo": {"today": None}}}]
                }
            }
        }

        with pytest.raises(
            RuntimeError,
            match="No prices available for today in Tibber API response",
        ):
            tibber.load_prices_from_tibber()


@patch("tibber.load_token")
def test_load_prices_returns_prices_when_valid_response(mock_load_token):
    mock_load_token.return_value = "dummy_token"
    with patch("tibber.load_data_from_tibber") as mock_load:
        mock_load.return_value = {
            "data": {
                "viewer": {
                    "homes": [
                        {
                            "currentSubscription": {
                                "priceInfo": {
                                    "today": [
                                        {"total": 0.5, "startsAt": "2025-12-11T00:00:00"},
                                        {"total": 0.6, "startsAt": "2025-12-11T00:15:00"},
                                        {"total": 0.7, "startsAt": "2025-12-11T00:30:00"},
                                    ]
                                }
                            }
                        }
                    ]
                }
            }
        }

        prices = tibber.load_prices_from_tibber()
        assert prices == [0.5, 0.6, 0.7]


@patch("tibber.load_token")
def test_load_stats_raises_error_when_no_homes_in_response(mock_load_token):
    mock_load_token.return_value = "dummy_token"
    with patch("tibber.load_data_from_tibber") as mock_load:
        mock_load.return_value = {"data": {"viewer": {"homes": []}}}

        with pytest.raises(
            RuntimeError, match="No homes found in Tibber API response"
        ):
            tibber.load_day_stats_from_tibber()


@patch("tibber.load_token")
def test_load_stats_handles_missing_production_data(mock_load_token):
    mock_load_token.return_value = "dummy_token"
    today_str = datetime.now().strftime('%Y-%m-%dT10:00:00+00:00')
    with patch("tibber.load_data_from_tibber") as mock_load:
        mock_load.return_value = {
            "data": {
                "viewer": {
                    "homes": [
                        {
                            "consumption": {
                                "nodes": [
                                    {
                                        "from": today_str,
                                        "to": today_str,
                                        "cost": 1.5,
                                        "consumption": 2.0,
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }

        stats = tibber.load_day_stats_from_tibber()
        assert stats["production"] == 0
        assert stats["profit"] == 0
        assert stats["consumption"] == 2.0
        assert stats["cost"] == 1.5


@patch("tibber.load_token")
def test_load_stats_handles_missing_consumption_data(mock_load_token):
    mock_load_token.return_value = "dummy_token"
    today_str = datetime.now().strftime('%Y-%m-%dT10:00:00+00:00')
    with patch("tibber.load_data_from_tibber") as mock_load:
        mock_load.return_value = {
            "data": {
                "viewer": {
                    "homes": [
                        {
                            "production": {
                                "nodes": [
                                    {
                                        "from": today_str,
                                        "to": today_str,
                                        "profit": 3.5,
                                        "production": 4.0,
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }

        stats = tibber.load_day_stats_from_tibber()
        assert stats["production"] == 4.0
        assert stats["profit"] == 3.5
        assert stats["consumption"] == 0
        assert stats["cost"] == 0
