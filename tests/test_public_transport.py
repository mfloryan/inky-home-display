import pytest
from datetime import datetime
from unittest.mock import patch, Mock
from public_transport import get_morning_departures, get_morning_departures_cached


@pytest.mark.parametrize(
    "hour_outside_morning_commute",
    [6, 11, 14, 23],
)
def test_returns_no_departures_outside_morning_hours(hour_outside_morning_commute):
    now = datetime(2025, 11, 8, hour_outside_morning_commute, 0, 0)
    departures = get_morning_departures(now=now)

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
                "stop_area": {"name": "Lahällsviadukten"},
            }
        ]
    }
    mock_get.return_value = mock_response

    now = datetime(2025, 11, 8, 8, 0, 0)
    departures = get_morning_departures(now=now)

    expected = [
        {
            "stop_name": "Lahällsviadukten",
            "destination": "Danderyds sjukhus",
            "line_number": "605",
            "scheduled_time": datetime(2025, 11, 8, 8, 17, 36),
            "transport_mode": "BUS",
            "journey_state": "EXPECTED",
            "walk_time_minutes": 6,
            "is_missed": False,
        }
    ]

    assert departures == expected


@patch("public_transport.requests.get")
def test_filters_only_bus_605_to_danderyds_sjukhus(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {
        "departures": [
            {
                "destination": "Sollentuna station",
                "scheduled": "2025-11-08T08:02:11",
                "line": {"designation": "627", "transport_mode": "BUS"},
                "journey": {"id": 111, "state": "EXPECTED"},
                "stop_area": {"name": "Lahällsviadukten"},
            },
            {
                "destination": "Danderyds sjukhus",
                "scheduled": "2025-11-08T08:17:36",
                "line": {"designation": "605", "transport_mode": "BUS"},
                "journey": {"id": 222, "state": "EXPECTED"},
                "stop_area": {"name": "Lahällsviadukten"},
            },
            {
                "destination": "Gribbylund",
                "scheduled": "2025-11-08T08:23:23",
                "line": {"designation": "605", "transport_mode": "BUS"},
                "journey": {"id": 333, "state": "EXPECTED"},
                "stop_area": {"name": "Lahällsviadukten"},
            },
        ]
    }
    mock_get.return_value = mock_response

    now = datetime(2025, 11, 8, 8, 0, 0)
    departures = get_morning_departures(now=now)

    expected = [
        {
            "stop_name": "Lahällsviadukten",
            "destination": "Danderyds sjukhus",
            "line_number": "605",
            "scheduled_time": datetime(2025, 11, 8, 8, 17, 36),
            "transport_mode": "BUS",
            "journey_state": "EXPECTED",
            "walk_time_minutes": 6,
            "is_missed": False,
        }
    ]

    assert departures == expected


@patch("public_transport.requests.get")
def test_returns_departures_from_both_stops(mock_get):
    def mock_api_response(url):
        response = Mock()
        if "2216" in url:
            response.json.return_value = {
                "departures": [
                    {
                        "destination": "Danderyds sjukhus",
                        "scheduled": "2025-11-08T08:17:36",
                        "line": {"designation": "605", "transport_mode": "BUS"},
                        "journey": {"id": 123, "state": "EXPECTED"},
                        "stop_area": {"name": "Lahällsviadukten"},
                    }
                ]
            }
        elif "9633" in url:
            response.json.return_value = {
                "departures": [
                    {
                        "destination": "Stockholms östra",
                        "scheduled": "2025-11-08T08:15:00",
                        "line": {"designation": "27", "transport_mode": "TRAM"},
                        "journey": {"id": 456, "state": "NORMALPROGRESS"},
                        "stop_area": {"name": "Roslags Näsby"},
                    }
                ]
            }
        return response

    mock_get.side_effect = mock_api_response

    now = datetime(2025, 11, 8, 8, 0, 0)
    departures = get_morning_departures(now=now)

    expected = [
        {
            "stop_name": "Roslags Näsby",
            "destination": "Stockholms östra",
            "line_number": "27",
            "scheduled_time": datetime(2025, 11, 8, 8, 15, 0),
            "transport_mode": "TRAM",
            "journey_state": "NORMALPROGRESS",
            "walk_time_minutes": 10,
            "is_missed": False,
        },
        {
            "stop_name": "Lahällsviadukten",
            "destination": "Danderyds sjukhus",
            "line_number": "605",
            "scheduled_time": datetime(2025, 11, 8, 8, 17, 36),
            "transport_mode": "BUS",
            "journey_state": "EXPECTED",
            "walk_time_minutes": 6,
            "is_missed": False,
        },
    ]

    assert departures == expected


@patch("public_transport.requests.get")
def test_marks_departures_as_missed_when_scheduled_within_walk_time(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {
        "departures": [
            {
                "destination": "Danderyds sjukhus",
                "scheduled": "2025-11-08T08:04:00",
                "line": {"designation": "605", "transport_mode": "BUS"},
                "journey": {"id": 111, "state": "EXPECTED"},
                "stop_area": {"name": "Lahällsviadukten"},
            },
            {
                "destination": "Danderyds sjukhus",
                "scheduled": "2025-11-08T08:10:00",
                "line": {"designation": "605", "transport_mode": "BUS"},
                "journey": {"id": 222, "state": "EXPECTED"},
                "stop_area": {"name": "Lahällsviadukten"},
            },
        ]
    }
    mock_get.return_value = mock_response

    now = datetime(2025, 11, 8, 8, 0, 0)
    departures = get_morning_departures(now=now)

    expected = [
        {
            "stop_name": "Lahällsviadukten",
            "destination": "Danderyds sjukhus",
            "line_number": "605",
            "scheduled_time": datetime(2025, 11, 8, 8, 4, 0),
            "transport_mode": "BUS",
            "journey_state": "EXPECTED",
            "walk_time_minutes": 6,
            "is_missed": True,
        },
        {
            "stop_name": "Lahällsviadukten",
            "destination": "Danderyds sjukhus",
            "line_number": "605",
            "scheduled_time": datetime(2025, 11, 8, 8, 10, 0),
            "transport_mode": "BUS",
            "journey_state": "EXPECTED",
            "walk_time_minutes": 6,
            "is_missed": False,
        },
    ]

    assert departures == expected


@patch("public_transport.requests.get")
def test_filters_departures_beyond_30_minutes(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {
        "departures": [
            {
                "destination": "Danderyds sjukhus",
                "scheduled": "2025-11-08T08:15:00",
                "line": {"designation": "605", "transport_mode": "BUS"},
                "journey": {"id": 111, "state": "EXPECTED"},
                "stop_area": {"name": "Lahällsviadukten"},
            },
            {
                "destination": "Danderyds sjukhus",
                "scheduled": "2025-11-08T08:25:00",
                "line": {"designation": "605", "transport_mode": "BUS"},
                "journey": {"id": 222, "state": "EXPECTED"},
                "stop_area": {"name": "Lahällsviadukten"},
            },
            {
                "destination": "Danderyds sjukhus",
                "scheduled": "2025-11-08T08:45:00",
                "line": {"designation": "605", "transport_mode": "BUS"},
                "journey": {"id": 333, "state": "EXPECTED"},
                "stop_area": {"name": "Lahällsviadukten"},
            },
        ]
    }
    mock_get.return_value = mock_response

    now = datetime(2025, 11, 8, 8, 0, 0)
    departures = get_morning_departures(now=now)

    assert len(departures) == 2
    assert departures[0]["scheduled_time"] == datetime(2025, 11, 8, 8, 15, 0)
    assert departures[1]["scheduled_time"] == datetime(2025, 11, 8, 8, 25, 0)


@patch("public_transport.requests.get")
def test_always_returns_at_least_one_departure_even_beyond_30_minutes(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {
        "departures": [
            {
                "destination": "Danderyds sjukhus",
                "scheduled": "2025-11-08T08:45:00",
                "line": {"designation": "605", "transport_mode": "BUS"},
                "journey": {"id": 111, "state": "EXPECTED"},
                "stop_area": {"name": "Lahällsviadukten"},
            },
            {
                "destination": "Danderyds sjukhus",
                "scheduled": "2025-11-08T09:00:00",
                "line": {"designation": "605", "transport_mode": "BUS"},
                "journey": {"id": 222, "state": "EXPECTED"},
                "stop_area": {"name": "Lahällsviadukten"},
            },
        ]
    }
    mock_get.return_value = mock_response

    now = datetime(2025, 11, 8, 8, 0, 0)
    departures = get_morning_departures(now=now)

    assert len(departures) == 1
    assert departures[0]["scheduled_time"] == datetime(2025, 11, 8, 8, 45, 0)


@patch("public_transport.cache")
@patch("public_transport.get_morning_departures")
def test_caches_with_10_minute_intervals(mock_get_departures, mock_cache):
    mock_cache.return_value = []

    now = datetime(2025, 11, 8, 8, 17, 30)
    get_morning_departures_cached(now=now)

    mock_cache.assert_called_once()
    cache_key = mock_cache.call_args[0][0]
    assert cache_key == "sl-departures-20251108-0810"


@patch("public_transport.cache")
@patch("public_transport.get_morning_departures")
def test_cache_key_rounds_to_10_minute_intervals(mock_get_departures, mock_cache):
    mock_cache.return_value = []

    test_times = [
        (datetime(2025, 11, 8, 8, 0, 0), "sl-departures-20251108-0800"),
        (datetime(2025, 11, 8, 8, 9, 59), "sl-departures-20251108-0800"),
        (datetime(2025, 11, 8, 8, 10, 0), "sl-departures-20251108-0810"),
        (datetime(2025, 11, 8, 8, 19, 30), "sl-departures-20251108-0810"),
        (datetime(2025, 11, 8, 8, 20, 0), "sl-departures-20251108-0820"),
    ]

    for now, expected_key in test_times:
        mock_cache.reset_mock()
        get_morning_departures_cached(now=now)
        cache_key = mock_cache.call_args[0][0]
        assert cache_key == expected_key
