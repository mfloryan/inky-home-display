import datetime
from dataclasses import dataclass

from fonts import FontLoader
from widgets.base import DrawProtocol, Rectangle, Widget


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
        temperature_right = 110

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
