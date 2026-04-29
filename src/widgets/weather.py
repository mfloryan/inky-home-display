import datetime
from dataclasses import dataclass

from fonts import FontLoader
from icons import load_icon
from widgets.base import DrawProtocol, Rectangle, Widget


@dataclass
class ForecastItem:
    time: datetime.datetime
    temp: float
    icon: str


@dataclass
class WeatherViewData:
    name: str
    sunrise: datetime.datetime
    sunset: datetime.datetime
    now_temp: float
    now_icon: str
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
        temperature_right = 110

        draw.text((20, 0), "POGODA", font=font_header, fill=colours[1])
        draw.text((20, 14), data.name, font=font_label, fill=colours[0])
        draw.ellipse([(6, 30), (17, 41)], fill=colours[1])
        draw.text(
            (20, 30),
            f"{data.sunrise.strftime('%H:%M')}-{data.sunset.strftime('%H:%M')}",
            font=font_sun,
            fill=colours[0],
        )

        draw.paste_image(load_icon(data.now_icon, 32), (0, 44))
        temp_text = f"{round(data.now_temp, 1)}°C"
        draw.text(
            (temperature_right - int(draw.textlength(temp_text, font=font_temp)), 50),
            temp_text,
            font=font_temp,
            fill=colours[0],
        )

        icon_h = 16
        y = 84
        for forecast in data.forecast[:4]:
            icon_bottom = y + icon_h

            time_str = forecast.time.strftime("%H:%M")
            time_h = draw.textbbox((0, 0), time_str, font=font_header)[3]
            draw.text(
                (0, icon_bottom - time_h), time_str, font=font_header, fill=colours[0]
            )

            draw.paste_image(load_icon(forecast.icon, 16), (54, y))

            temp_text = f"{round(forecast.temp)}°C"
            temp_h = draw.textbbox((0, 0), temp_text, font=font_temp)[3]
            draw.text(
                (
                    temperature_right - int(draw.textlength(temp_text, font=font_temp)),
                    icon_bottom - temp_h,
                ),
                temp_text,
                font=font_temp,
                fill=colours[0],
            )

            y += 24
