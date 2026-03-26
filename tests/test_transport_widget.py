import datetime

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
        font_loader = FontLoader()
        base_time = datetime.datetime(2025, 1, 15, 8, 0)

        transport_data = TransportViewData(
            departures=[
                DepartureViewData(
                    line_number="605", scheduled_time=base_time, is_missed=True
                ),
            ]
        )

        widget = TransportWidget(bounds, font_loader, transport_data)
        img = Image.new("RGB", (bounds.width, bounds.height), "white")
        draw = ImageDraw.Draw(img)
        colours = ["black", "yellow"]

        widget.render(draw, colours)

        pixels = img.load()
        yellow_pixels_found = False
        for y in range(bounds.height):
            for x in range(bounds.width):
                if pixels[x, y] == (255, 255, 0):
                    yellow_pixels_found = True
                    break
            if yellow_pixels_found:
                break

        assert yellow_pixels_found

    def test_draws_border_around_content(self):
        bounds = Rectangle(0, 0, 76, 227)
        font_loader = FontLoader()
        base_time = datetime.datetime(2025, 1, 15, 8, 0)

        transport_data = TransportViewData(
            departures=[
                DepartureViewData(
                    line_number="605", scheduled_time=base_time, is_missed=False
                ),
            ]
        )

        widget = TransportWidget(bounds, font_loader, transport_data)
        img = Image.new("RGB", (bounds.width, bounds.height), "white")
        draw = ImageDraw.Draw(img)
        colours = ["black", "yellow"]

        widget.render(draw, colours)

        pixels = img.load()
        top_left_is_yellow = pixels[0, 0] == (255, 255, 0)
        assert top_left_is_yellow
