import datetime
from unittest.mock import MagicMock

from display_backend import PngFileBackend
from widgets import ForecastItem, Rectangle, WeatherViewData, WeatherWidget


class TestWeatherWidget:
    def test_weather_widget_renders_header_and_location(self):
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
        # Mock textlength to return a fixed value so we can verify centering logic if needed
        mock_draw.textlength.return_value = 40

        backend = PngFileBackend()
        colours = backend.colors

        widget.render(mock_draw, colours)

        text_calls = [call[0] for call in mock_draw.text.call_args_list]

        # Verify "POGODA" header
        header_call = next(c for c in text_calls if c[1] == "POGODA")
        assert header_call[0][1] == 0  # y coordinate

        # Verify location name
        location_call = next(c for c in text_calls if c[1] == "Stockholm")
        assert location_call[0][1] == 14  # y coordinate

    def test_weather_widget_renders_current_conditions(self):
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

        # Check current temperature
        text_calls = [call[0] for call in mock_draw.text.call_args_list]
        assert any("2.5°C" in c[1] for c in text_calls)

        # Check current icon bitmap
        bitmap_calls = [call[0] for call in mock_draw.bitmap.call_args_list]
        assert any(c[0] == (5, 44) for c in bitmap_calls)

    def test_weather_widget_renders_forecast_items(self):
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
        # Mock textbbox for height calculations
        mock_draw.textbbox.return_value = (0, 0, 10, 10)

        backend = PngFileBackend()
        colours = backend.colors

        widget.render(mock_draw, colours)

        # Should have 1 current icon + 2 forecast icons
        bitmap_calls = mock_draw.bitmap.call_args_list
        assert len(bitmap_calls) == 3

        # Verify forecast times and temperatures are rendered
        text_content = [call[0][1] for call in mock_draw.text.call_args_list]
        assert "18:00" in text_content
        assert "21:00" in text_content
        assert "1°C" in text_content
        assert "-1°C" in text_content

    def test_weather_widget_handles_empty_forecast(self):
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
        widget.render(mock_draw, [0, 1, 2])

        # Only 1 bitmap (current weather)
        assert mock_draw.bitmap.call_count == 1


def _make_weather_data(**kwargs):
    defaults = dict(
        name="Stockholm",
        sunrise=datetime.datetime(2023, 12, 25, 8, 30),
        sunset=datetime.datetime(2023, 12, 25, 15, 45),
        now_temp=2.5,
        now_icon="01d",
        forecast=[],
    )
    return WeatherViewData(**{**defaults, **kwargs})


class WhenWeatherDataIncludesHeatpumpOutdoorTemp:
    def it_renders_the_zewn_label_with_temperature(self):
        weather_data = _make_weather_data(heatpump_outdoor_temp=11.2)
        mock_draw = MagicMock()
        mock_draw.textlength.return_value = 40

        WeatherWidget(Rectangle(0, 0, 120, 200), MagicMock(), weather_data).render(
            mock_draw, PngFileBackend().colors
        )

        text_content = [call[0][1] for call in mock_draw.text.call_args_list]
        assert any("zewn." in t and "11.2°" in t for t in text_content)

    def it_does_not_render_zewn_line_when_temp_is_absent(self):
        weather_data = _make_weather_data(heatpump_outdoor_temp=None)
        mock_draw = MagicMock()
        mock_draw.textlength.return_value = 40

        WeatherWidget(Rectangle(0, 0, 120, 200), MagicMock(), weather_data).render(
            mock_draw, PngFileBackend().colors
        )

        text_content = [call[0][1] for call in mock_draw.text.call_args_list]
        assert not any("zewn." in t for t in text_content)

    def it_starts_forecast_items_lower_when_heatpump_temp_is_shown(self):
        forecast = [ForecastItem(time=datetime.datetime(2023, 12, 25, 18, 0), temp=1, icon="03d")]
        weather_data_with = _make_weather_data(heatpump_outdoor_temp=11.2, forecast=forecast)
        weather_data_without = _make_weather_data(heatpump_outdoor_temp=None, forecast=forecast)

        def forecast_y(weather_data):
            mock_draw = MagicMock()
            mock_draw.textlength.return_value = 10
            mock_draw.textbbox.return_value = (0, 0, 10, 10)
            WeatherWidget(Rectangle(0, 0, 120, 200), MagicMock(), weather_data).render(
                mock_draw, PngFileBackend().colors
            )
            bitmap_calls = mock_draw.bitmap.call_args_list
            return bitmap_calls[-1][0][0][1]

        assert forecast_y(weather_data_with) > forecast_y(weather_data_without)
