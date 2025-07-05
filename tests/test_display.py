import datetime
from unittest.mock import MagicMock

from display import Rectangle, HeaderWidget, EnergyStatsWidget, EnergyData
from display_backend import PngFileBackend


class TestHeaderWidget:
    def test_header_widget_renders_polish_date_at_widget_origin(self):

        bounds = Rectangle(4, 0, 396, 25)
        current_time = datetime.datetime(2023, 12, 25, 14, 30)
        widget = HeaderWidget(bounds, current_time)

        mock_draw = MagicMock()
        backend = PngFileBackend()
        colours = backend.colors

        widget.render(mock_draw, colours)

        mock_draw.text.assert_called_once()
        call_args = mock_draw.text.call_args

        # Widget should draw at its own origin (0,0)
        assert call_args[0][0] == (0, 0)
        # Should use black color
        assert call_args[1]["fill"] == colours[0]
        # Should render Polish date format for Monday, December 25, 2023
        text_content = call_args[0][1]
        assert "poniedziałek 25 grudnia 2023" == text_content.lower()


class TestEnergyStatsWidget:
    def test_energy_stats_widget_renders_production_and_consumption_at_widget_origin(self):
        bounds = Rectangle(270, 28, 130, 28)
        energy_data = EnergyData(
            production=2.5,
            consumption=1.8,
            profit=1.25,
            cost=0.95
        )
        widget = EnergyStatsWidget(bounds, energy_data)

        mock_draw = MagicMock()
        backend = PngFileBackend()
        colours = backend.colors

        widget.render(mock_draw, colours)

        assert mock_draw.text.call_count == 2
        calls = mock_draw.text.call_args_list

        # First call should be production line at (0, 0)
        production_call = calls[0]
        assert production_call[0][0] == (0, 0)
        assert "do sieci 2.5 kWh +1.25 SEK" == production_call[0][1]
        assert production_call[1]["anchor"] == "ra"
        assert production_call[1]["fill"] == colours[0]

        # Second call should be consumption line at (0, 14)
        consumption_call = calls[1]
        assert consumption_call[0][0] == (0, 14)
        assert "z sieci 1.8 kWh -0.95 SEK" == consumption_call[0][1]
        assert consumption_call[1]["anchor"] == "ra"
        assert consumption_call[1]["fill"] == colours[0]
