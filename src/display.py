import datetime
import math
import locale
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol
from PIL import ImageDraw
from display_backend import create_backend
from fonts import FontLoader


@dataclass
class Rectangle:
    x: int
    y: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.x + self.width

    @property
    def bottom(self) -> int:
        return self.y + self.height


class DrawProtocol(Protocol):
    def text(self, xy, text, **kwargs): ...
    def rectangle(self, xy, **kwargs): ...
    def textlength(self, text, **kwargs) -> float: ...


class TranslatedDraw:
    def __init__(self, draw: DrawProtocol, offset_x: int, offset_y: int):
        self.draw = draw
        self.offset_x = offset_x
        self.offset_y = offset_y

    def text(self, xy, text, **kwargs):
        translated_xy = (xy[0] + self.offset_x, xy[1] + self.offset_y)
        return self.draw.text(translated_xy, text, **kwargs)

    def rectangle(self, xy, **kwargs):
        if len(xy) == 4:
            translated_xy = [
                xy[0] + self.offset_x,
                xy[1] + self.offset_y,
                xy[2] + self.offset_x,
                xy[3] + self.offset_y,
            ]
        else:
            translated_xy = [
                (xy[0][0] + self.offset_x, xy[0][1] + self.offset_y),
                (xy[1][0] + self.offset_x, xy[1][1] + self.offset_y),
            ]
        return self.draw.rectangle(translated_xy, **kwargs)

    def textlength(self, text, **kwargs):
        return self.draw.textlength(text, **kwargs)


class Widget(ABC):
    def __init__(self, bounds: Rectangle):
        self.bounds = bounds

    @abstractmethod
    def render(self, draw: DrawProtocol, colours: list) -> None:
        pass


class HeaderWidget(Widget):
    def __init__(
        self,
        bounds: Rectangle,
        font_loader: FontLoader,
        current_time: datetime.datetime,
    ):
        super().__init__(bounds)
        self.font_loader = font_loader
        self.current_time = current_time

    def render(self, draw: DrawProtocol, colours: list) -> None:
        locale.setlocale(locale.LC_ALL, "pl_PL.utf8")
        font = self.font_loader.ubuntu_regular(22)
        date_text = self.current_time.strftime("%A %d %B %Y")
        draw.text((0, 0), date_text, font=font, fill=colours[0])


@dataclass
class EnergyData:
    production: float
    consumption: float
    profit: float
    cost: float


@dataclass
class EnergyPriceData:
    day_hourly_prices: list[float]
    current_hour: int


class EnergyStatsWidget(Widget):
    def __init__(
        self, bounds: Rectangle, font_loader: FontLoader, energy_data: EnergyData
    ):
        super().__init__(bounds)
        self.font_loader = font_loader
        self.energy_data = energy_data

    def render(self, draw: DrawProtocol, colours: list) -> None:
        font = self.font_loader.ubuntu_regular(11)
        production_text = f"do sieci {round(self.energy_data.production, 2)} kWh {self.energy_data.profit:+.2f} SEK"
        consumption_text = f"z sieci {round(self.energy_data.consumption, 2)} kWh {(-1) * self.energy_data.cost:+.2f} SEK"

        draw.text((0, 0), production_text, font=font, fill=colours[0], anchor="ra")
        draw.text((0, 14), consumption_text, font=font, fill=colours[0], anchor="ra")


class EnergyPriceLabelsWidget(Widget):
    def __init__(
        self, bounds: Rectangle, font_loader: FontLoader, price_data: EnergyPriceData
    ):
        super().__init__(bounds)
        self.font_loader = font_loader
        self.price_data = price_data

    def render(self, draw: DrawProtocol, colours: list) -> None:
        hourly_price_max = max(self.price_data.day_hourly_prices)
        hourly_price_min = min(self.price_data.day_hourly_prices)

        font_bold = self.font_loader.terminus_bold_16()
        font = self.font_loader.terminus_regular_12()

        price_range_text = (
            f"{round(hourly_price_min, 2)} -- {round(hourly_price_max, 2)} SEK"
        )
        draw.text((0, 0), price_range_text, font=font, fill=colours[0])

        now_price_baseline = 14
        now_price_left = 0
        now_price_text = f"now: {round(self.price_data.day_hourly_prices[self.price_data.current_hour], 2)} SEK"
        draw.rectangle(
            [
                (now_price_left - 2, now_price_baseline - 1),
                (
                    now_price_left
                    - 2
                    + draw.textlength(now_price_text, font=font_bold)
                    + 2,
                    now_price_baseline + 13,
                ),
            ],
            outline=colours[1],
            width=1,
        )
        draw.text(
            (now_price_left, now_price_baseline),
            now_price_text,
            font=font_bold,
            fill=colours[0],
        )


def draw_energy_price_graph(
    draw, colours, day_hourly_prices, current_time, font_loader
):
    min_dim = {"x": 6, "y": 60}
    max_dim = {"x": 270, "y": 284}
    draw.rectangle(
        [min_dim["x"], min_dim["y"], max_dim["x"], max_dim["y"]], outline=colours[0]
    )

    hourly_price_max = max(day_hourly_prices)
    hourly_price_min = min(day_hourly_prices)

    _draw_price_reference_lines(draw, colours, hourly_price_max, min_dim, max_dim)
    _draw_hourly_price_bars(
        draw, colours, day_hourly_prices, min_dim, max_dim, current_time
    )
    _draw_price_labels(
        draw,
        colours,
        day_hourly_prices,
        hourly_price_min,
        hourly_price_max,
        current_time,
        font_loader,
    )


def _draw_price_reference_lines(draw, colours, hourly_price_max, min_dim, max_dim):
    dy = max_dim["y"] - min_dim["y"] - 2
    if hourly_price_max > 1.0:
        highest_full_sek = math.floor(hourly_price_max)
        one_sek_step = round(
            ((highest_full_sek * dy) / hourly_price_max) / highest_full_sek
        )

        for y in range(highest_full_sek):
            for x in range(min_dim["x"] + 1, max_dim["x"]):
                if x % 2 == 0:
                    draw.point(
                        [x, max_dim["y"] - (one_sek_step * (y + 1))], fill=colours[0]
                    )


def _draw_hourly_price_bars(
    draw, colours, day_hourly_prices, min_dim, max_dim, current_time
):
    dy = max_dim["y"] - min_dim["y"] - 2
    dx = max_dim["x"] - min_dim["x"]
    bar_width = round(dx / len(day_hourly_prices))
    hourly_price_max = max(day_hourly_prices)
    hourly_price_min = min(day_hourly_prices)
    max_abs_price = max(abs(hourly_price_max), abs(hourly_price_min), 1.0)

    for hour, hourly_price in enumerate(day_hourly_prices):
        bar_left = (bar_width * hour + min_dim["x"]) + 2
        bar_right = (bar_width * (hour + 1) + min_dim["x"]) - 2

        if hourly_price >= 0:
            bar_top = max_dim["y"] - round(dy * (hourly_price / max_abs_price))
            bar_bottom = max_dim["y"]
        else:
            bar_top = min_dim["y"]
            bar_bottom = min_dim["y"] + round(dy * (abs(hourly_price) / max_abs_price))

        if current_time.hour == hour:
            draw.rectangle(
                [bar_left - 2, min_dim["y"] + 1, bar_right + 2, max_dim["y"] - 1],
                fill=colours[1],
            )

        draw.rectangle([bar_left, bar_top, bar_right, bar_bottom], fill=colours[0])


def _draw_price_labels(
    draw,
    colours,
    day_hourly_prices,
    hourly_price_min,
    hourly_price_max,
    current_time,
    font_loader,
):
    font_bold = font_loader.terminus_bold_16()
    font = font_loader.terminus_regular_12()

    price_range_text = (
        f"{round(hourly_price_min, 2)} -- {round(hourly_price_max, 2)} SEK"
    )
    draw.text((10, 28), price_range_text, font=font, fill=colours[0])

    now_price_baseline = 42
    now_price_left = 10
    now_price_text = f"now: {round(day_hourly_prices[current_time.hour], 2)} SEK"
    draw.rectangle(
        [
            (now_price_left - 2, now_price_baseline - 1),
            (
                now_price_left
                - 2
                + draw.textlength(now_price_text, font=font_bold)
                + 2,
                now_price_baseline + 13,
            ),
        ],
        outline=colours[1],
        width=1,
    )
    draw.text(
        (now_price_left, now_price_baseline),
        now_price_text,
        font=font_bold,
        fill=colours[0],
    )


def draw_weather(draw, colours, data, font_loader):
    font_sun = font_loader.terminus_regular_12()
    font_header = font_loader.terminus_bold_14()
    font_temp = font_loader.terminus_bold_22()
    font_label = font_loader.ubuntu_regular(12)
    temperature_right = 390

    def draw_single_forecast(forecast, y):
        draw.text(
            (280, y),
            forecast["time"].strftime("%H:%M"),
            font=font_header,
            fill=colours[0],
        )
        temp_text = f"{round(forecast['temp'])}°C"
        draw.text(
            (temperature_right - draw.textlength(temp_text, font=font_temp), y - 6),
            temp_text,
            font=font_temp,
            fill=colours[0],
        )
        y += 12
        draw.text((280, y), forecast["weather"], font=font_label, fill=colours[0])
        y += 26
        return y

    draw.text((300, 6), "POGODA", font=font_header, fill=colours[1])
    draw.text((300, 20), data["name"], font=font_label, fill=colours[0])
    draw.ellipse([(286, 36), (297, 47)], fill=colours[1])
    draw.text(
        (300, 36),
        f"{data['sunrise'].strftime('%H:%M')}-{data['sunset'].strftime('%H:%M')}",
        font=font_sun,
        fill=colours[0],
    )
    temp_text = f"{round(data['now']['temp'], 1)}°C"
    draw.text(
        (temperature_right - draw.textlength(temp_text, font=font_temp), 50),
        temp_text,
        font=font_temp,
        fill=colours[0],
    )
    draw.text((280, 55), "teraz:", font=font_label, fill=colours[1])

    forecast_y = 86
    for forecast in data["forecast"][:4]:
        forecast_y = draw_single_forecast(forecast, forecast_y)


def generate_content(draw, data, colours):
    font_loader = FontLoader()

    header_widget = HeaderWidget(
        Rectangle(4, 0, 396, 25), font_loader, data["current_time"]
    )
    translated_draw = TranslatedDraw(
        draw, header_widget.bounds.x, header_widget.bounds.y
    )
    header_widget.render(translated_draw, colours)

    locale.setlocale(locale.LC_ALL, "pl_PL.utf8")

    if data["energy_prices"]:
        draw_energy_price_graph(
            draw, colours, data["energy_prices"], data["current_time"], font_loader
        )

    if data["energy_stats"]:
        energy_data = EnergyData(
            production=data["energy_stats"]["production"],
            consumption=data["energy_stats"]["consumption"],
            profit=data["energy_stats"]["profit"],
            cost=data["energy_stats"]["cost"],
        )
        energy_stats_widget = EnergyStatsWidget(
            Rectangle(270, 28, 400 - 270, 100), font_loader, energy_data
        )
        translated_draw = TranslatedDraw(
            draw, energy_stats_widget.bounds.x, energy_stats_widget.bounds.y
        )
        energy_stats_widget.render(translated_draw, colours)

    if data["weather"]:
        draw_weather(draw, colours, data["weather"], font_loader)

    locale.setlocale(locale.LC_ALL, "en_GB.utf8")
    font = font_loader.terminus_regular_12()
    now_text = "Updated: " + data["current_time"].strftime("%c")
    now_size = draw.textbbox((0, 0), now_text, font=font)
    draw.text(
        (400 - now_size[2], 300 - now_size[3]), now_text, font=font, fill=colours[1]
    )


def display(data, prefer_inky=True, png_output_path="img/test.png"):
    backend = create_backend(prefer_inky, png_output_path)

    img = backend.create_image()
    draw = ImageDraw.Draw(img)
    colours = backend.colors

    generate_content(draw, data, colours)
    backend.show(img)
