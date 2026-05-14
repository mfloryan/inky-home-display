import pytest
from unittest.mock import AsyncMock, patch

from data.thermia import get_outdoor_temp, _decode_signed_16bit


class WhenDecodingSignedTemperatureValues:
    def it_returns_positive_values_unchanged(self):
        assert _decode_signed_16bit(1080) == 1080

    def it_decodes_negative_values_from_twos_complement(self):
        assert _decode_signed_16bit(0xFB50) == -1200

    def it_treats_zero_as_zero(self):
        assert _decode_signed_16bit(0) == 0

    def it_treats_max_positive_value_as_positive(self):
        assert _decode_signed_16bit(0x7FFF) == 32767

    def it_treats_0x8000_as_the_most_negative_value(self):
        assert _decode_signed_16bit(0x8000) == -32768


class WhenReadingOutdoorTemperature:
    def it_returns_temperature_scaled_to_celsius(self):
        mock_client = AsyncMock()
        mock_client.read_input_registers = AsyncMock(return_value=[1080])

        with patch("data.thermia.tmodbus.create_async_tcp_client", return_value=mock_client):
            result = get_outdoor_temp()

        assert result == pytest.approx(10.80)

    def it_returns_negative_temperature_correctly(self):
        mock_client = AsyncMock()
        mock_client.read_input_registers = AsyncMock(return_value=[0xFB50])

        with patch("data.thermia.tmodbus.create_async_tcp_client", return_value=mock_client):
            result = get_outdoor_temp()

        assert result == pytest.approx(-12.0)

    def it_reads_from_the_outdoor_register_address(self):
        mock_client = AsyncMock()
        mock_client.read_input_registers = AsyncMock(return_value=[500])

        with patch("data.thermia.tmodbus.create_async_tcp_client", return_value=mock_client):
            get_outdoor_temp()

        mock_client.read_input_registers.assert_awaited_once_with(start_address=13, quantity=1)

    def it_returns_none_when_the_connection_fails(self):
        with patch(
            "data.thermia.tmodbus.create_async_tcp_client",
            side_effect=ConnectionError("refused"),
        ):
            result = get_outdoor_temp()

        assert result is None

    def it_returns_none_when_the_modbus_read_fails(self):
        mock_client = AsyncMock()
        mock_client.read_input_registers = AsyncMock(side_effect=Exception("read timeout"))

        with patch("data.thermia.tmodbus.create_async_tcp_client", return_value=mock_client):
            result = get_outdoor_temp()

        assert result is None
