import datetime
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
    def textbbox(self, xy, text, **kwargs) -> tuple[float, float, float, float]: ...
    def point(self, xy, **kwargs): ...
    def ellipse(self, xy, **kwargs): ...


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

    def textbbox(self, xy, text, **kwargs):
        return self.draw.textbbox(xy, text, **kwargs)

    def point(self, xy, **kwargs):
        translated_xy = (xy[0] + self.offset_x, xy[1] + self.offset_y)
        return self.draw.point(translated_xy, **kwargs)

    def ellipse(self, xy, **kwargs):
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
        return self.draw.ellipse(translated_xy, **kwargs)


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
    day_prices: list[float]
    current_quarter: int


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
        price_max = max(self.price_data.day_prices)
        price_min = min(self.price_data.day_prices)

        font_bold = self.font_loader.terminus_bold_16()
        font = self.font_loader.terminus_regular_12()

        price_range_text = f"{round(price_min, 2)} -- {round(price_max, 2)} SEK"
        draw.text((0, 0), price_range_text, font=font, fill=colours[0])

        now_price_baseline = 14
        now_price_left = 0
        now_price_text = f"now: {round(self.price_data.day_prices[self.price_data.current_quarter], 2)} SEK"
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


class FooterWidget(Widget):
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
        locale.setlocale(locale.LC_ALL, "en_GB.utf8")
        font = self.font_loader.terminus_regular_12()
        now_text = "Updated: " + self.current_time.strftime("%c")
        now_size = draw.textbbox((0, 0), now_text, font=font)

        x = self.bounds.width - now_size[2]
        y = self.bounds.height - now_size[3]
        draw.text((x, y), now_text, font=font, fill=colours[1])


class EnergyPriceGraphWidget(Widget):
    def __init__(self, bounds: Rectangle, price_data: EnergyPriceData):
        super().__init__(bounds)
        self.price_data = price_data

    def render(self, draw: DrawProtocol, colours: list) -> None:
        draw.rectangle(
            [0, 0, self.bounds.width, self.bounds.height], outline=colours[0]
        )

        price_max = max(self.price_data.day_prices)
        self._draw_reference_lines(draw, colours, price_max)
        self._draw_price_bars(draw, colours)

    def _draw_reference_lines(
        self, draw: DrawProtocol, colours: list, price_max: float
    ) -> None:
        dy = self.bounds.height - 2
        if price_max > 1.0:
            highest_full_sek = int(price_max)
            one_sek_step = round(
                ((highest_full_sek * dy) / price_max) / highest_full_sek
            )

            for y in range(highest_full_sek):
                for x in range(1, self.bounds.width):
                    if x % 2 == 0:
                        draw.point(
                            [x, self.bounds.height - (one_sek_step * (y + 1))],
                            fill=colours[0],
                        )

    def _draw_price_bars(self, draw: DrawProtocol, colours: list) -> None:
        dy = self.bounds.height - 2
        bar_width = 1
        bar_spacing = 1
        price_max = max(self.price_data.day_prices)
        price_min = min(self.price_data.day_prices)
        max_abs_price = max(abs(price_max), abs(price_min), 1.0)

        for index, price in enumerate(self.price_data.day_prices):
            bar_left = (bar_width + bar_spacing) * (index + 1)
            bar_right = bar_left + bar_width - 1

            if price >= 0:
                bar_top = self.bounds.height - round(dy * (price / max_abs_price))
                bar_bottom = self.bounds.height
            else:
                bar_top = 0
                bar_bottom = round(dy * (abs(price) / max_abs_price))

            if self.price_data.current_quarter == index:
                draw.rectangle(
                    [bar_left - 1, 1, bar_right + 1, self.bounds.height - 1],
                    fill=colours[1],
                )

            draw.rectangle([bar_left, bar_top, bar_right, bar_bottom], fill=colours[0])


@dataclass
class ForecastItem:
    time: datetime.datetime
    temp: float
    weather: str


@dataclass
class WeatherViewData:
    name: str
    sunrise: datetime.datetime
    sunset: datetime.datetime
    now_temp: float
    forecast: list[ForecastItem]


class WeatherWidget(Widget):
    def __init__(self, bounds: Rectangle, font_loader: FontLoader, weather_data: WeatherViewData):
        super().__init__(bounds)
        self.font_loader = font_loader
        self.weather_data = weather_data

    def render(self, draw: DrawProtocol, colours: list) -> None:
        data = self.weather_data
        font_sun = self.font_loader.terminus_regular_12()
        font_header = self.font_loader.terminus_bold_14()
        font_temp = self.font_loader.terminus_bold_22()
        font_label = self.font_loader.ubuntu_regular(12)
        temperature_right = 110  # Adjusted for widget bounds

        def draw_single_forecast(forecast, y):
            draw.text(
                (0, y),
                forecast.time.strftime("%H:%M"),
                font=font_header,
                fill=colours[0],
            )
            temp_text = f"{round(forecast.temp)}°C"
            draw.text(
                (temperature_right - draw.textlength(temp_text, font=font_temp), y - 6),
                temp_text,
                font=font_temp,
                fill=colours[0],
            )
            y += 12
            draw.text((0, y), forecast.weather, font=font_label, fill=colours[0])
            y += 26
            return y

        draw.text((20, 0), "POGODA", font=font_header, fill=colours[1])
        draw.text((20, 14), data.name, font=font_label, fill=colours[0])
        draw.ellipse([(6, 30), (17, 41)], fill=colours[1])
        draw.text(
            (20, 30),
            f"{data.sunrise.strftime('%H:%M')}-{data.sunset.strftime('%H:%M')}",
            font=font_sun,
            fill=colours[0],
        )
        temp_text = f"{round(data.now_temp, 1)}°C"
        draw.text(
            (temperature_right - draw.textlength(temp_text, font=font_temp), 44),
            temp_text,
            font=font_temp,
            fill=colours[0],
        )
        draw.text((0, 49), "teraz:", font=font_label, fill=colours[1])

        forecast_y = 80
        for forecast in data.forecast[:4]:
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
        price_data = EnergyPriceData(
            day_prices=data["energy_prices"],
            current_quarter=(data["current_time"].hour * 4)
            + (data["current_time"].minute // 15),
        )

        num_bars = len(data["energy_prices"])
        bar_width = 1
        bar_spacing = 1
        graph_width = (num_bars * (bar_width + bar_spacing)) + 2
        energy_price_graph_widget = EnergyPriceGraphWidget(
            Rectangle(6, 60, graph_width, 200), price_data
        )
        translated_draw = TranslatedDraw(
            draw, energy_price_graph_widget.bounds.x, energy_price_graph_widget.bounds.y
        )
        energy_price_graph_widget.render(translated_draw, colours)

        price_labels_widget = EnergyPriceLabelsWidget(
            Rectangle(10, 28, 260, 30), font_loader, price_data
        )
        translated_draw = TranslatedDraw(
            draw, price_labels_widget.bounds.x, price_labels_widget.bounds.y
        )
        price_labels_widget.render(translated_draw, colours)

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
        weather_view_data = WeatherViewData(
            name=data["weather"]["name"],
            sunrise=data["weather"]["sunrise"],
            sunset=data["weather"]["sunset"],
            now_temp=data["weather"]["now"]["temp"],
            forecast=[
                ForecastItem(
                    time=forecast["time"],
                    temp=forecast["temp"],
                    weather=forecast["weather"]
                )
                for forecast in data["weather"]["forecast"]
            ]
        )
        weather_widget = WeatherWidget(
            Rectangle(280, 6, 120, 200), font_loader, weather_view_data
        )
        translated_draw = TranslatedDraw(
            draw, weather_widget.bounds.x, weather_widget.bounds.y
        )
        weather_widget.render(translated_draw, colours)

    footer_widget = FooterWidget(
        Rectangle(200, 287, 200, 13), font_loader, data["current_time"]
    )
    translated_draw = TranslatedDraw(
        draw, footer_widget.bounds.x, footer_widget.bounds.y
    )
    footer_widget.render(translated_draw, colours)


def display(data, prefer_inky=True, png_output_path="img/test.png"):
    backend = create_backend(prefer_inky, png_output_path)

    img = backend.create_image()
    draw = ImageDraw.Draw(img)
    colours = backend.colors

    generate_content(draw, data, colours)
    backend.show(img)
