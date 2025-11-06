from datetime import datetime, timedelta
from unittest.mock import patch
from public_transport import (
    get_morning_departures,
    get_morning_departures_cached,
    _filter_lahallsviadukten_departures,
    _filter_roslags_nasby_departures,
    _apply_time_window_filter,
)


class TestMorningDepartures:
    @patch("public_transport.datetime")
    @patch("public_transport._fetch_departures_from_site")
    def test_should_return_empty_list_when_outside_morning_hours(
        self, mock_fetch, mock_datetime
    ):
        # Arrange
        mock_now = datetime(2025, 11, 6, 13, 30)
        mock_datetime.now.return_value = mock_now

        # Act
        result = get_morning_departures()

        # Assert
        assert result == []
        mock_fetch.assert_not_called()

    @patch("public_transport.datetime")
    @patch("public_transport._fetch_departures_from_site")
    def test_should_fetch_departures_from_both_stops_during_morning_hours(
        self, mock_fetch, mock_datetime
    ):
        # Arrange
        mock_now = datetime(2025, 11, 6, 8, 30)
        mock_datetime.now.return_value = mock_now
        mock_fetch.return_value = []

        # Act
        get_morning_departures()

        # Assert
        assert mock_fetch.call_count == 2
        mock_fetch.assert_any_call(2216)  # Lahällsviadukten
        mock_fetch.assert_any_call(9633)  # Roslags Näsby

    @patch("public_transport.datetime")
    @patch("public_transport._fetch_departures_from_site")
    def test_should_return_sorted_departures_by_scheduled_time(
        self, mock_fetch, mock_datetime
    ):
        # Arrange
        mock_now = datetime(2025, 11, 6, 8, 0)
        mock_datetime.now.return_value = mock_now

        lahalls_raw = [
            {
                "line": {"designation": "605", "transport_mode": "BUS"},
                "destination": "Danderyds sjukhus",
                "scheduled": "2025-11-06T08:30:00",
                "journey": {"id": 1, "state": "EXPECTED", "prediction_state": "NORMAL"},
            }
        ]

        nasby_raw = [
            {
                "line": {"designation": "27", "transport_mode": "TRAM"},
                "direction": "Stockholms östra",
                "scheduled": "2025-11-06T08:15:00",
                "journey": {"id": 2, "state": "NORMALPROGRESS", "prediction_state": "NORMAL"},
            }
        ]

        def fetch_side_effect(site_id):
            if site_id == 2216:
                return lahalls_raw
            else:
                return nasby_raw

        mock_fetch.side_effect = fetch_side_effect

        # Act
        result = get_morning_departures()

        # Assert
        assert len(result) == 2
        assert result[0]["stop_name"] == "Roslags Näsby"
        assert result[0]["scheduled_time"] == datetime(2025, 11, 6, 8, 15)
        assert result[1]["stop_name"] == "Lahällsviadukten"
        assert result[1]["scheduled_time"] == datetime(2025, 11, 6, 8, 30)


class TestLahallsviaduktenFiltering:
    def test_should_filter_only_bus_605_to_danderyds_sjukhus(self):
        # Arrange
        raw_departures = [
            {
                "line": {"designation": "605", "transport_mode": "BUS"},
                "destination": "Danderyds sjukhus",
                "scheduled": "2025-11-06T08:30:00",
                "journey": {"id": 1, "state": "EXPECTED", "prediction_state": "NORMAL"},
            },
            {
                "line": {"designation": "605", "transport_mode": "BUS"},
                "destination": "Gribbylund",
                "scheduled": "2025-11-06T08:35:00",
                "journey": {"id": 2, "state": "EXPECTED", "prediction_state": "NORMAL"},
            },
            {
                "line": {"designation": "619", "transport_mode": "BUS"},
                "destination": "Danderyds sjukhus",
                "scheduled": "2025-11-06T08:40:00",
                "journey": {"id": 3, "state": "EXPECTED", "prediction_state": "NORMAL"},
            },
        ]

        # Act
        with patch("public_transport.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 11, 6, 8, 0)
            result = _filter_lahallsviadukten_departures(raw_departures, 6)

        # Assert
        assert len(result) == 1
        assert result[0]["line_number"] == "605"
        assert result[0]["destination"] == "Danderyds sjukhus"

    def test_should_mark_departure_as_missed_when_within_walk_time(self):
        # Arrange
        raw_departures = [
            {
                "line": {"designation": "605", "transport_mode": "BUS"},
                "destination": "Danderyds sjukhus",
                "scheduled": "2025-11-06T08:04:00",
                "journey": {"id": 1, "state": "EXPECTED", "prediction_state": "NORMAL"},
            }
        ]

        # Act
        with patch("public_transport.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 11, 6, 8, 0)
            result = _filter_lahallsviadukten_departures(raw_departures, 6)

        # Assert
        assert result[0]["is_missed"] is True

    def test_should_mark_departure_as_not_missed_when_beyond_walk_time(self):
        # Arrange
        raw_departures = [
            {
                "line": {"designation": "605", "transport_mode": "BUS"},
                "destination": "Danderyds sjukhus",
                "scheduled": "2025-11-06T08:10:00",
                "journey": {"id": 1, "state": "EXPECTED", "prediction_state": "NORMAL"},
            }
        ]

        # Act
        with patch("public_transport.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 11, 6, 8, 0)
            result = _filter_lahallsviadukten_departures(raw_departures, 6)

        # Assert
        assert result[0]["is_missed"] is False

    def test_should_include_all_required_fields_in_departure(self):
        # Arrange
        raw_departures = [
            {
                "line": {"designation": "605", "transport_mode": "BUS"},
                "destination": "Danderyds sjukhus",
                "scheduled": "2025-11-06T08:30:00",
                "journey": {
                    "id": 2025110600123,
                    "state": "EXPECTED",
                    "prediction_state": "NORMAL"
                },
            }
        ]

        # Act
        with patch("public_transport.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 11, 6, 8, 0)
            result = _filter_lahallsviadukten_departures(raw_departures, 6)

        # Assert
        departure = result[0]
        assert departure["stop_name"] == "Lahällsviadukten"
        assert departure["line_number"] == "605"
        assert departure["destination"] == "Danderyds sjukhus"
        assert departure["scheduled_time"] == datetime(2025, 11, 6, 8, 30)
        assert departure["walk_time_minutes"] == 6
        assert "is_missed" in departure
        assert departure["transport_mode"] == "BUS"
        assert departure["journey_state"] == "EXPECTED"
        assert departure["journey"]["id"] == 2025110600123
        assert departure["journey"]["state"] == "EXPECTED"
        assert departure["journey"]["prediction_state"] == "NORMAL"


class TestRoslagsNasbyFiltering:
    def test_should_filter_only_trains_to_stockholms_ostra(self):
        # Arrange
        raw_departures = [
            {
                "line": {"designation": "27", "transport_mode": "TRAM"},
                "direction": "Stockholms östra",
                "scheduled": "2025-11-06T08:15:00",
                "journey": {"id": 1, "state": "EXPECTED", "prediction_state": "NORMAL"},
            },
            {
                "line": {"designation": "28", "transport_mode": "TRAM"},
                "direction": "Stockholms östra",
                "scheduled": "2025-11-06T08:20:00",
                "journey": {"id": 2, "state": "EXPECTED", "prediction_state": "NORMAL"},
            },
            {
                "line": {"designation": "27", "transport_mode": "TRAM"},
                "direction": "Kårsta",
                "scheduled": "2025-11-06T08:25:00",
                "journey": {"id": 3, "state": "EXPECTED", "prediction_state": "NORMAL"},
            },
            {
                "line": {"designation": "605", "transport_mode": "BUS"},
                "direction": "Stockholms östra",
                "scheduled": "2025-11-06T08:30:00",
                "journey": {"id": 4, "state": "EXPECTED", "prediction_state": "NORMAL"},
            },
        ]

        # Act
        with patch("public_transport.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 11, 6, 8, 0)
            result = _filter_roslags_nasby_departures(raw_departures, 10)

        # Assert
        assert len(result) == 2
        assert all(dep["destination"] == "Stockholms östra" for dep in result)
        assert result[0]["line_number"] == "27"
        assert result[1]["line_number"] == "28"

    def test_should_mark_departure_as_missed_when_within_walk_time(self):
        # Arrange
        raw_departures = [
            {
                "line": {"designation": "27", "transport_mode": "TRAM"},
                "direction": "Stockholms östra",
                "scheduled": "2025-11-06T08:08:00",
                "journey": {"id": 1, "state": "EXPECTED", "prediction_state": "NORMAL"},
            }
        ]

        # Act
        with patch("public_transport.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 11, 6, 8, 0)
            result = _filter_roslags_nasby_departures(raw_departures, 10)

        # Assert
        assert result[0]["is_missed"] is True

    def test_should_include_all_required_fields_in_departure(self):
        # Arrange
        raw_departures = [
            {
                "line": {"designation": "27", "transport_mode": "TRAM"},
                "direction": "Stockholms östra",
                "scheduled": "2025-11-06T08:15:00",
                "journey": {
                    "id": 2025110600456,
                    "state": "NORMALPROGRESS",
                    "prediction_state": "NORMAL"
                },
            }
        ]

        # Act
        with patch("public_transport.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 11, 6, 8, 0)
            result = _filter_roslags_nasby_departures(raw_departures, 10)

        # Assert
        departure = result[0]
        assert departure["stop_name"] == "Roslags Näsby"
        assert departure["line_number"] == "27"
        assert departure["destination"] == "Stockholms östra"
        assert departure["scheduled_time"] == datetime(2025, 11, 6, 8, 15)
        assert departure["walk_time_minutes"] == 10
        assert departure["transport_mode"] == "TRAM"
        assert departure["journey_state"] == "NORMALPROGRESS"
        assert departure["journey"]["id"] == 2025110600456
        assert departure["journey"]["state"] == "NORMALPROGRESS"
        assert departure["journey"]["prediction_state"] == "NORMAL"


class TestTimeWindowFilter:
    def test_should_return_empty_list_when_no_departures(self):
        # Arrange
        departures = []

        # Act
        result = _apply_time_window_filter(departures)

        # Assert
        assert result == []

    def test_should_return_all_departures_within_30_minute_window(self):
        # Arrange
        now = datetime(2025, 11, 6, 8, 0)
        departures = [
            {"scheduled_time": now + timedelta(minutes=10)},
            {"scheduled_time": now + timedelta(minutes=20)},
            {"scheduled_time": now + timedelta(minutes=30)},
        ]

        # Act
        with patch("public_transport.datetime") as mock_datetime:
            mock_datetime.now.return_value = now
            result = _apply_time_window_filter(departures)

        # Assert
        assert len(result) == 3

    def test_should_exclude_departures_beyond_30_minute_window(self):
        # Arrange
        now = datetime(2025, 11, 6, 8, 0)
        departures = [
            {"scheduled_time": now + timedelta(minutes=10)},
            {"scheduled_time": now + timedelta(minutes=20)},
            {"scheduled_time": now + timedelta(minutes=35)},
            {"scheduled_time": now + timedelta(minutes=45)},
        ]

        # Act
        with patch("public_transport.datetime") as mock_datetime:
            mock_datetime.now.return_value = now
            result = _apply_time_window_filter(departures)

        # Assert
        assert len(result) == 2

    def test_should_return_at_least_one_departure_when_all_beyond_window(self):
        # Arrange
        now = datetime(2025, 11, 6, 8, 0)
        departures = [
            {"scheduled_time": now + timedelta(minutes=45)},
            {"scheduled_time": now + timedelta(minutes=60)},
        ]

        # Act
        with patch("public_transport.datetime") as mock_datetime:
            mock_datetime.now.return_value = now
            result = _apply_time_window_filter(departures)

        # Assert
        assert len(result) == 1
        assert result[0]["scheduled_time"] == now + timedelta(minutes=45)


class TestCachedDepartures:
    @patch("public_transport.cache")
    @patch("public_transport.datetime")
    def test_should_cache_with_15_minute_rounded_key(self, mock_datetime, mock_cache):
        # Arrange
        mock_now = datetime(2025, 11, 6, 8, 17)
        mock_datetime.now.return_value = mock_now
        mock_cache.return_value = []

        # Act
        get_morning_departures_cached()

        # Assert
        expected_key = "sl-departures-20251106-0815"
        mock_cache.assert_called_once()
        assert mock_cache.call_args[0][0] == expected_key

    @patch("public_transport.cache")
    @patch("public_transport.datetime")
    def test_should_serialize_datetime_objects_for_caching(
        self, mock_datetime, mock_cache
    ):
        # Arrange
        mock_now = datetime(2025, 11, 6, 8, 0)
        mock_datetime.now.return_value = mock_now

        cached_data = [
            {
                "stop_name": "Roslags Näsby",
                "line_number": "27",
                "destination": "Stockholms östra",
                "scheduled_time": "2025-11-06T08:15:00",
                "walk_time_minutes": 10,
                "is_missed": False,
            }
        ]
        mock_cache.return_value = cached_data

        # Act
        result = get_morning_departures_cached()

        # Assert
        assert isinstance(result[0]["scheduled_time"], datetime)
        assert result[0]["scheduled_time"] == datetime(2025, 11, 6, 8, 15)
