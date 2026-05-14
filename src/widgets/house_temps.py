from dataclasses import dataclass

from fonts import FontLoader
from widgets.base import DrawProtocol, Rectangle, Widget


@dataclass
class HouseTempReading:
    label: str
    temp: float


@dataclass
class HouseTempsViewData:
    readings: list[HouseTempReading]


class HouseTempsWidget(Widget):
    def __init__(
        self, bounds: Rectangle, font_loader: FontLoader, data: HouseTempsViewData
    ):
        super().__init__(bounds)
        self.font_loader = font_loader
        self.data = data

    def render(self, draw: DrawProtocol, colours: list) -> None:
        font_header = self.font_loader.terminus_bold_14()
        font_label = self.font_loader.terminus_regular_12()
        font_temp = self.font_loader.terminus_bold_14()

        header = "DOM"
        header_x = (self.bounds.width - draw.textlength(header, font=font_header)) / 2
        draw.text((header_x, 0), header, font=font_header, fill=colours[1])

        y = 16
        for reading in self.data.readings:
            draw.text((0, y), reading.label, font=font_label, fill=colours[0])
            temp_str = f"{reading.temp:.1f}°C"
            temp_x = self.bounds.width - draw.textlength(temp_str, font=font_temp)
            draw.text((temp_x, y), temp_str, font=font_temp, fill=colours[0])
            y += 20
