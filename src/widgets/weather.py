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
    heatpump_outdoor_temp: float | None = None


class WeatherWidget(Widget):
    def __init__(
        self, bounds: Rectangle, font_loader: FontLoader, weather_data: WeatherViewData
    ):
        super().__init__(bounds)
        self.font_loader = font_loader
        self.weather_data = weather_data

    def render(self, draw: DrawProtocol, colours: list) -> None:
        data = self.weather_data
        font_sun = self.font_loader.terminus_regular_12()
        font_header = self.font_loader.terminus_bold_14()
        font_temp = self.font_loader.terminus_bold_22()
        font_temp_small = self.font_loader.terminus_bold(18)
        font_time_small = self.font_loader.terminus_regular_12()
        font_label = self.font_loader.ubuntu_regular(12)
        temperature_right = 110

        def draw_centered_text(text, font, y, color):
            text_width = draw.textlength(text, font=font)
            x = (self.bounds.width - text_width) / 2
            draw.text((x, y), text, font=font, fill=color)

        draw_centered_text("POGODA", font_header, 0, colours[1])
        draw_centered_text(data.name, font_label, 14, colours[0])
        draw.ellipse([(1, 30), (12, 41)], fill=colours[1])
        draw_centered_text(
            f"{data.sunrise.strftime('%H:%M')}-{data.sunset.strftime('%H:%M')}",
            font_sun,
            30,
            colours[0],
        )

        draw.bitmap((5, 44), load_icon(data.now_icon, 32), fill=colours[0])
        temp_text = f"{round(data.now_temp, 1)}°C"
        draw.text(
            (temperature_right - int(draw.textlength(temp_text, font=font_temp)), 50),
            temp_text,
            font=font_temp,
            fill=colours[0],
        )

        y = 84
        if data.heatpump_outdoor_temp is not None:
            font_hp_temp = self.font_loader.terminus_bold_16()
            hp_temp = f"{data.heatpump_outdoor_temp:.1f}°C"
            hp_temp_x = temperature_right - int(draw.textlength(hp_temp, font=font_hp_temp))
            hp_label = "zewn."
            hp_label_x = hp_temp_x - int(draw.textlength(hp_label, font=font_sun)) - 2
            draw.text((hp_label_x, 78), hp_label, font=font_sun, fill=colours[0])
            draw.text((hp_temp_x, 76), hp_temp, font=font_hp_temp, fill=colours[1])
            y = 92

        icon_h = 16
        for forecast in data.forecast[:4]:
            icon_bottom = y + icon_h

            time_str = forecast.time.strftime("%H:%M")
            time_h = draw.textbbox((0, 0), time_str, font=font_time_small)[3]
            draw.text(
                (0, icon_bottom - time_h),
                time_str,
                font=font_time_small,
                fill=colours[0],
            )

            draw.bitmap((35, y), load_icon(forecast.icon, 16), fill=colours[0])

            temp_text = f"{round(forecast.temp)}°C"
            temp_h = draw.textbbox((0, 0), temp_text, font=font_temp_small)[3]
            draw.text(
                (
                    temperature_right
                    - int(draw.textlength(temp_text, font=font_temp_small)),
                    icon_bottom - temp_h,
                ),
                temp_text,
                font=font_temp_small,
                fill=colours[0],
            )

            y += 24
