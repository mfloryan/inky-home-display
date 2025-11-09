import datetime
from dataclasses import dataclass

from fonts import FontLoader
from widgets.base import DrawProtocol, Rectangle, Widget


@dataclass
class DepartureViewData:
    line_number: str
    scheduled_time: datetime.datetime
    is_missed: bool


@dataclass
class TransportViewData:
    departures: list[DepartureViewData]


class TransportWidget(Widget):
    def __init__(
        self, bounds: Rectangle, font_loader: FontLoader, transport_data: TransportViewData
    ):
        super().__init__(bounds)
        self.font_loader = font_loader
        self.transport_data = transport_data

    def render(self, draw: DrawProtocol, colours: list) -> None:
        font_header = self.font_loader.terminus_bold_14()
        font_line = self.font_loader.terminus_bold_16()
        font_time = self.font_loader.terminus_regular_12()

        draw.text((2, 2), "TRANSPORT", font=font_header, fill=colours[1])

        y = 20
        line_height = 20

        for departure in self.transport_data.departures:
            draw.text((2, y), departure.line_number, font=font_line, fill=colours[0])

            time_text = departure.scheduled_time.strftime("%H:%M")
            time_colour = colours[1] if departure.is_missed else colours[0]
            time_width = draw.textlength(time_text, font=font_time)
            draw.text(
                (self.bounds.width - time_width - 2, y), time_text, font=font_time, fill=time_colour
            )

            y += line_height

        content_bottom = y + 2
        draw.rectangle(
            [0, 0, self.bounds.width - 1, content_bottom], outline=colours[1]
        )
