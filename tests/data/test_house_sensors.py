from unittest.mock import Mock, patch

from data.house_sensors import get_house_temperatures


class WhenFetchingHouseTemperatures:
    def it_returns_temperatures_for_configured_sensors(self):
        mock_response = Mock()
        mock_response.json.return_value = {
            "readings": [
                {"name": "sensor-up", "temperature": 22.2},
                {"name": "sensor-master-bedroom", "temperature": 20.1},
                {"name": "sensor-kitchen", "temperature": 22.8},
                {"name": "sensor-other", "temperature": 19.0},
            ]
        }
        with patch("data.house_sensors.requests.get", return_value=mock_response):
            result = get_house_temperatures()

        assert result == [
            {"label": "Salon", "temp": 22.2},
            {"label": "Sypialnia", "temp": 20.1},
            {"label": "Kuchnia", "temp": 22.8},
        ]

    def it_preserves_the_configured_display_order_regardless_of_api_order(self):
        mock_response = Mock()
        mock_response.json.return_value = {
            "readings": [
                {"name": "sensor-kitchen", "temperature": 22.8},
                {"name": "sensor-up", "temperature": 22.2},
                {"name": "sensor-master-bedroom", "temperature": 20.1},
            ]
        }
        with patch("data.house_sensors.requests.get", return_value=mock_response):
            result = get_house_temperatures()

        assert [r["label"] for r in result] == ["Salon", "Sypialnia", "Kuchnia"]

    def it_returns_only_available_sensors_when_some_are_missing_from_response(self):
        mock_response = Mock()
        mock_response.json.return_value = {
            "readings": [
                {"name": "sensor-up", "temperature": 22.2},
                {"name": "sensor-kitchen", "temperature": 22.8},
            ]
        }
        with patch("data.house_sensors.requests.get", return_value=mock_response):
            result = get_house_temperatures()

        assert result == [
            {"label": "Salon", "temp": 22.2},
            {"label": "Kuchnia", "temp": 22.8},
        ]

    def it_returns_none_when_no_configured_sensors_are_present_in_response(self):
        mock_response = Mock()
        mock_response.json.return_value = {
            "readings": [{"name": "sensor-other", "temperature": 18.0}]
        }
        with patch("data.house_sensors.requests.get", return_value=mock_response):
            result = get_house_temperatures()

        assert result is None

    def it_returns_none_when_the_request_fails(self):
        with patch("data.house_sensors.requests.get", side_effect=Exception("timeout")):
            result = get_house_temperatures()

        assert result is None
