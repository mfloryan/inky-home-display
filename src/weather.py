import functools
from datetime import datetime

import requests

from tokens import read_token_file


@functools.lru_cache(maxsize=1)
def load_token():
    return read_token_file("openweather-api-token", "Unable to load Open Weather token")


def get_weather():
    def parse_forecast(item):
        return {
            "time": datetime.fromtimestamp(item["dt"]),
            "temp": item["main"]["temp"],
            "icon": item["weather"][0]["icon"],
        }

    payload = {
        "lat": "59.4308",
        "lon": "18.0637",
        "units": "metric",
        "appid": load_token(),
    }

    r = requests.get(
        "https://api.openweathermap.org/data/2.5/weather", params=payload, timeout=10
    )
    current_weather = r.json()
    weather = {
        "name": current_weather["name"],
        "sunrise": datetime.fromtimestamp(current_weather["sys"]["sunrise"]),
        "sunset": datetime.fromtimestamp(current_weather["sys"]["sunset"]),
        "now": {
            "temp": current_weather["main"]["temp"],
            "icon": current_weather["weather"][0]["icon"],
        },
    }

    forecast_payload = payload | {"cnt": 8}
    r = requests.get(
        "https://api.openweathermap.org/data/2.5/forecast",
        params=forecast_payload,
        timeout=10,
    )
    forecast = r.json()
    weather["forecast"] = list(map(parse_forecast, forecast["list"]))
    return weather
