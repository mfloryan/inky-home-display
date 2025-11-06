from unittest.mock import MagicMock

from display_backend import PngFileBackend
from widgets import (
    EnergyData,
    EnergyPriceData,
    EnergyPriceGraphWidget,
    EnergyPriceLabelsWidget,
    EnergyStatsWidget,
    Rectangle,
)


class TestEnergyStatsWidget:
    def test_energy_stats_widget_renders_production_and_consumption_at_widget_origin(
        self,
    ):
        bounds = Rectangle(270, 28, 130, 28)
        energy_data = EnergyData(
            production=2.5, consumption=1.8, profit=1.25, cost=0.95
        )
        mock_font_loader = MagicMock()
        widget = EnergyStatsWidget(bounds, mock_font_loader, energy_data)

        mock_draw = MagicMock()
        backend = PngFileBackend()
        colours = backend.colors

        widget.render(mock_draw, colours)

        assert mock_draw.text.call_count == 2
        calls = mock_draw.text.call_args_list

        production_call = calls[0]
        assert production_call[0][0] == (0, 0)
        assert "do sieci 2.5 kWh +1.25 SEK" == production_call[0][1]
        assert production_call[1]["anchor"] == "ra"
        assert production_call[1]["fill"] == colours[0]

        consumption_call = calls[1]
        assert consumption_call[0][0] == (0, 14)
        assert "z sieci 1.8 kWh -0.95 SEK" == consumption_call[0][1]
        assert consumption_call[1]["anchor"] == "ra"
        assert consumption_call[1]["fill"] == colours[0]


class TestEnergyPriceLabelsWidget:
    def test_energy_price_labels_widget_renders_range_and_current_price(self):
        bounds = Rectangle(10, 28, 260, 30)
        price_data = EnergyPriceData(
            day_prices=[0.85, 0.92, 1.15, 1.22, 1.18, 0.95], current_quarter=2
        )
        mock_font_loader = MagicMock()
        widget = EnergyPriceLabelsWidget(bounds, mock_font_loader, price_data)

        mock_draw = MagicMock()
        backend = PngFileBackend()
        colours = backend.colors

        widget.render(mock_draw, colours)

        assert mock_draw.text.call_count == 2
        assert mock_draw.rectangle.call_count == 1

        text_calls = mock_draw.text.call_args_list
        rect_call = mock_draw.rectangle.call_args

        range_call = text_calls[0]
        assert range_call[0][0] == (0, 0)
        assert "0.85 -- 1.22 SEK" == range_call[0][1]
        assert range_call[1]["fill"] == colours[0]

        assert rect_call[1]["outline"] == colours[1]
        assert rect_call[1]["width"] == 1

        current_call = text_calls[1]
        assert current_call[0][0] == (0, 14)
        assert "now: 1.15 SEK" == current_call[0][1]
        assert current_call[1]["fill"] == colours[0]


class TestEnergyPriceGraphWidget:
    def test_energy_price_graph_widget_renders_bars_and_highlights_current_hour(self):
        bounds = Rectangle(6, 60, 264, 224)
        price_data = EnergyPriceData(
            day_prices=[0.5, 0.8, 1.2, 0.9, 0.6], current_quarter=2
        )
        widget = EnergyPriceGraphWidget(bounds, price_data)

        mock_draw = MagicMock()
        backend = PngFileBackend()
        colours = backend.colors

        widget.render(mock_draw, colours)

        assert mock_draw.rectangle.call_count >= 1
        assert mock_draw.point.call_count >= 1

        first_rect_call = mock_draw.rectangle.call_args_list[0]
        assert first_rect_call[0][0] == [0, 0, 264, 224]
        assert first_rect_call[1]["outline"] == colours[0]
