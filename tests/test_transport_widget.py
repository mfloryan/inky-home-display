import datetime

from unittest.mock import MagicMock

from PIL import Image, ImageDraw

from fonts import FontLoader
from widgets import DepartureViewData, Rectangle, TransportViewData, TransportWidget


class TestTransportWidget:
    def test_renders_departures_with_line_numbers_and_times(self):
        bounds = Rectangle(0, 0, 76, 227)
        font_loader = FontLoader()
        base_time = datetime.datetime(2025, 1, 15, 8, 0)

        transport_data = TransportViewData(
            departures=[
                DepartureViewData(
                    line_number="605", scheduled_time=base_time, is_missed=False
                ),
                DepartureViewData(
                    line_number="27",
                    scheduled_time=base_time + datetime.timedelta(minutes=10),
                    is_missed=False,
                ),
            ]
        )

        widget = TransportWidget(bounds, font_loader, transport_data)
        img = Image.new("RGB", (bounds.width, bounds.height), "white")
        draw = ImageDraw.Draw(img)
        colours = ["black", "yellow"]

        widget.render(draw, colours)

        pixels = img.load()
        assert pixels is not None

    def test_highlights_missed_departure_times_in_yellow(self):
        bounds = Rectangle(0, 0, 76, 227)
        font_loader = MagicMock()
        base_time = datetime.datetime(2025, 1, 15, 8, 0)

        transport_data = TransportViewData(
            departures=[
                DepartureViewData(
                    line_number="605", scheduled_time=base_time, is_missed=True
                ),
            ]
        )

        widget = TransportWidget(bounds, font_loader, transport_data)
        mock_draw = MagicMock()
        mock_draw.textlength.return_value = 10
        colours = ["black", "yellow"]

        widget.render(mock_draw, colours)

        # Expected parameters for the time text:
        # Time is "08:00"
        # X coord is bounds.width - 10 - 2 = 76 - 12 = 64
        # Y coord is 20
        # Font is font_loader.terminus_regular_12()
        expected_call = (
            (64, 20),
            "08:00",
        )
        # Check if any call matches our expectation
        found = False
        for call in mock_draw.text.call_args_list:
            args, kwargs = call
            if args == expected_call and kwargs.get('fill') == "yellow":
                found = True
                break

        assert found, "Expected mock_draw.text to be called with missed departure highlighted in yellow"

    def test_draws_border_around_content(self):
        bounds = Rectangle(0, 0, 76, 227)
        font_loader = MagicMock()
        base_time = datetime.datetime(2025, 1, 15, 8, 0)

        transport_data = TransportViewData(
            departures=[
                DepartureViewData(
                    line_number="605", scheduled_time=base_time, is_missed=False
                ),
            ]
        )

        widget = TransportWidget(bounds, font_loader, transport_data)
        mock_draw = MagicMock()
        mock_draw.textlength.return_value = 10
        colours = ["black", "yellow"]

        widget.render(mock_draw, colours)

        mock_draw.rectangle.assert_called_once_with(
            [0, 0, 75, 42], outline="yellow"
        )
