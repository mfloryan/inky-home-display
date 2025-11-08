import pytest
from datetime import time, datetime
from unittest.mock import patch, Mock
from public_transport import get_morning_departures


@pytest.mark.parametrize(
    "time_outside_morning_commute",
    [
        time(hour=6, minute=59),
        time(hour=11, minute=0),
        time(hour=14, minute=30),
        time(hour=23, minute=0),
    ],
)
def test_returns_no_departures_outside_morning_hours(time_outside_morning_commute):
    departures = get_morning_departures(now=time_outside_morning_commute)

    assert departures == []


@patch("public_transport.requests.get")
def test_fetches_departures_during_morning_hours(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {
        "departures": [
            {
                "destination": "Danderyds sjukhus",
                "scheduled": "2025-11-08T08:17:36",
                "line": {"designation": "605", "transport_mode": "BUS"},
                "journey": {"id": 123, "state": "EXPECTED"},
            }
        ]
    }
    mock_get.return_value = mock_response

    departures = get_morning_departures(now=time(hour=8))

    expected = [
        {
            "destination": "Danderyds sjukhus",
            "line_number": "605",
            "scheduled_time": datetime(2025, 11, 8, 8, 17, 36),
            "transport_mode": "BUS",
            "journey_state": "EXPECTED",
        }
    ]

    assert departures == expected
