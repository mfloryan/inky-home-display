import datetime
from unittest.mock import MagicMock

from display import (
    Rectangle,
    HeaderWidget,
    EnergyStatsWidget,
    EnergyData,
    EnergyPriceLabelsWidget,
    EnergyPriceData,
    FooterWidget,
    EnergyPriceGraphWidget,
    WeatherWidget,
)
from display_backend import PngFileBackend


class TestHeaderWidget:
    def test_header_widget_renders_polish_date_at_widget_origin(self):
        bounds = Rectangle(4, 0, 396, 25)
        current_time = datetime.datetime(2023, 12, 25, 14, 30)
        mock_font_loader = MagicMock()
        widget = HeaderWidget(bounds, mock_font_loader, current_time)

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


class TestEnergyPriceLabelsWidget:
    def test_energy_price_labels_widget_renders_range_and_current_price(self):
        bounds = Rectangle(10, 28, 260, 30)
        price_data = EnergyPriceData(
            day_hourly_prices=[0.85, 0.92, 1.15, 1.22, 1.18, 0.95], current_hour=2
        )
        mock_font_loader = MagicMock()
        widget = EnergyPriceLabelsWidget(bounds, mock_font_loader, price_data)

        mock_draw = MagicMock()
        backend = PngFileBackend()
        colours = backend.colors

        widget.render(mock_draw, colours)

        # Should have 3 calls: range text, current price box, current price text
        assert mock_draw.text.call_count == 2
        assert mock_draw.rectangle.call_count == 1

        text_calls = mock_draw.text.call_args_list
        rect_call = mock_draw.rectangle.call_args

        # First text call: price range at (0, 0)
        range_call = text_calls[0]
        assert range_call[0][0] == (0, 0)
        assert "0.85 -- 1.22 SEK" == range_call[0][1]
        assert range_call[1]["fill"] == colours[0]

        # Rectangle for current price box
        assert rect_call[1]["outline"] == colours[1]
        assert rect_call[1]["width"] == 1

        # Second text call: current price at (0, 14)
        current_call = text_calls[1]
        assert current_call[0][0] == (0, 14)
        assert "now: 1.15 SEK" == current_call[0][1]
        assert current_call[1]["fill"] == colours[0]


class TestFooterWidget:
    def test_footer_widget_renders_update_timestamp_at_bottom_right(self):
        bounds = Rectangle(200, 287, 200, 13)
        current_time = datetime.datetime(2023, 12, 25, 14, 30, 45)
        mock_font_loader = MagicMock()
        mock_font_loader.terminus_regular_12.return_value = "mock_font"
        widget = FooterWidget(bounds, mock_font_loader, current_time)

        mock_draw = MagicMock()
        mock_draw.textbbox.return_value = (0, 0, 150, 12)
        backend = PngFileBackend()
        colours = backend.colors

        widget.render(mock_draw, colours)

        mock_draw.text.assert_called_once()
        call_args = mock_draw.text.call_args

        # Should calculate position to right-align text
        assert call_args[0][0] == (50, 1)  # (200-150, 13-12)
        assert call_args[0][1] == "Updated: Mon 25 Dec 2023 14:30:45 "
        assert call_args[1]["fill"] == colours[1]  # Yellow color


class TestWeatherWidget:
    def test_weather_widget_renders_location_and_current_temperature_at_widget_origin(self):
        bounds = Rectangle(280, 6, 120, 200)
        weather_data = {
            "name": "Stockholm",
            "sunrise": datetime.datetime(2023, 12, 25, 8, 30),
            "sunset": datetime.datetime(2023, 12, 25, 15, 45),
            "now": {"temp": 2.5},
            "forecast": [
                {"time": datetime.datetime(2023, 12, 25, 18, 0), "temp": 1, "weather": "pochmurno"},
                {"time": datetime.datetime(2023, 12, 25, 21, 0), "temp": -1, "weather": "śnieg"},
            ]
        }
        mock_font_loader = MagicMock()
        widget = WeatherWidget(bounds, mock_font_loader, weather_data)

        mock_draw = MagicMock()
        backend = PngFileBackend()
        colours = backend.colors

        widget.render(mock_draw, colours)

        # Should render header "POGODA" at (20, 0) relative to widget origin
        text_calls = mock_draw.text.call_args_list
        pogoda_call = text_calls[0]
        assert pogoda_call[0][0] == (20, 0)
        assert pogoda_call[0][1] == "POGODA"
        assert pogoda_call[1]["fill"] == colours[1]

        # Should render location name at (20, 14)
        location_call = text_calls[1]
        assert location_call[0][0] == (20, 14)
        assert location_call[0][1] == "Stockholm"
        assert location_call[1]["fill"] == colours[0]


class TestEnergyPriceGraphWidget:
    def test_energy_price_graph_widget_renders_bars_and_highlights_current_hour(self):
        bounds = Rectangle(6, 60, 264, 224)
        price_data = EnergyPriceData(
            day_hourly_prices=[0.5, 0.8, 1.2, 0.9, 0.6], current_hour=2
        )
        widget = EnergyPriceGraphWidget(bounds, price_data)

        mock_draw = MagicMock()
        backend = PngFileBackend()
        colours = backend.colors

        widget.render(mock_draw, colours)

        # Should draw main rectangle outline
        assert mock_draw.rectangle.call_count >= 1

        # Should draw reference lines (points)
        assert mock_draw.point.call_count >= 1

        # First rectangle call should be the main graph outline
        first_rect_call = mock_draw.rectangle.call_args_list[0]
        assert first_rect_call[0][0] == [0, 0, 264, 224]
        assert first_rect_call[1]["outline"] == colours[0]
