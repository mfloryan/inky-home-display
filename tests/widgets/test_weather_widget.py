import datetime
from unittest.mock import MagicMock

from display_backend import PngFileBackend
from widgets import ForecastItem, Rectangle, WeatherViewData, WeatherWidget


class TestWeatherWidget:
    def test_weather_widget_renders_location_name_at_widget_origin(self):
        bounds = Rectangle(280, 6, 120, 200)
        weather_data = WeatherViewData(
            name="Stockholm",
            sunrise=datetime.datetime(2023, 12, 25, 8, 30),
            sunset=datetime.datetime(2023, 12, 25, 15, 45),
            now_temp=2.5,
            now_icon="01d",
            forecast=[
                ForecastItem(
                    time=datetime.datetime(2023, 12, 25, 18, 0), temp=1, icon="03d"
                ),
                ForecastItem(
                    time=datetime.datetime(2023, 12, 25, 21, 0), temp=-1, icon="13d"
                ),
            ],
        )
        mock_font_loader = MagicMock()
        widget = WeatherWidget(bounds, mock_font_loader, weather_data)

        mock_draw = MagicMock()
        backend = PngFileBackend()
        colours = backend.colors

        widget.render(mock_draw, colours)

        text_calls = mock_draw.text.call_args_list
        pogoda_call = text_calls[0]
        assert pogoda_call[0][0] == (20, 0)
        assert pogoda_call[0][1] == "POGODA"
        assert pogoda_call[1]["fill"] == colours[1]

        location_call = text_calls[1]
        assert location_call[0][0] == (20, 14)
        assert location_call[0][1] == "Stockholm"
        assert location_call[1]["fill"] == colours[0]

    def test_weather_widget_renders_icon_for_current_conditions(self):
        bounds = Rectangle(280, 6, 120, 200)
        weather_data = WeatherViewData(
            name="Stockholm",
            sunrise=datetime.datetime(2023, 12, 25, 8, 30),
            sunset=datetime.datetime(2023, 12, 25, 15, 45),
            now_temp=2.5,
            now_icon="01d",
            forecast=[
                ForecastItem(
                    time=datetime.datetime(2023, 12, 25, 18, 0), temp=1, icon="03d"
                ),
            ],
        )
        mock_font_loader = MagicMock()
        widget = WeatherWidget(bounds, mock_font_loader, weather_data)

        mock_draw = MagicMock()
        backend = PngFileBackend()
        colours = backend.colors

        widget.render(mock_draw, colours)

        bitmap_calls = mock_draw.bitmap.call_args_list
        assert bitmap_calls[0][0][0] == (0, 44)

    def test_weather_widget_renders_icons_for_each_forecast_entry(self):
        bounds = Rectangle(280, 6, 120, 200)
        weather_data = WeatherViewData(
            name="Stockholm",
            sunrise=datetime.datetime(2023, 12, 25, 8, 30),
            sunset=datetime.datetime(2023, 12, 25, 15, 45),
            now_temp=2.5,
            now_icon="01d",
            forecast=[
                ForecastItem(
                    time=datetime.datetime(2023, 12, 25, 18, 0), temp=1, icon="03d"
                ),
                ForecastItem(
                    time=datetime.datetime(2023, 12, 25, 21, 0), temp=-1, icon="13d"
                ),
            ],
        )
        mock_font_loader = MagicMock()
        widget = WeatherWidget(bounds, mock_font_loader, weather_data)

        mock_draw = MagicMock()
        backend = PngFileBackend()
        colours = backend.colors

        widget.render(mock_draw, colours)

        bitmap_calls = mock_draw.bitmap.call_args_list
        assert bitmap_calls[1][0][0] == (54, 84)
        assert bitmap_calls[2][0][0] == (54, 108)

    def test_weather_widget_does_not_render_teraz_label(self):
        bounds = Rectangle(280, 6, 120, 200)
        weather_data = WeatherViewData(
            name="Stockholm",
            sunrise=datetime.datetime(2023, 12, 25, 8, 30),
            sunset=datetime.datetime(2023, 12, 25, 15, 45),
            now_temp=2.5,
            now_icon="01d",
            forecast=[],
        )
        mock_font_loader = MagicMock()
        widget = WeatherWidget(bounds, mock_font_loader, weather_data)

        mock_draw = MagicMock()
        backend = PngFileBackend()
        colours = backend.colors

        widget.render(mock_draw, colours)

        text_calls = [call[0][1] for call in mock_draw.text.call_args_list]
        assert "teraz:" not in text_calls
