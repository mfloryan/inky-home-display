from datetime import datetime
import logging
import os

import requests


def load_token():
    try:
        file = open(
            os.path.join(os.path.dirname(__file__), "openweather-api-token"),
            "r",
            encoding="utf-8",
        )
    except FileNotFoundError as ex:
        logging.getLogger(__name__).error(
            "Token file `openweather-api-token` not found"
        )
        raise RuntimeError("Unable to load Open Weather token") from ex
    else:
        with file:
            return file.read()


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

    try:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/weather", params=payload, timeout=10
        )
        r.raise_for_status()
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
        r.raise_for_status()
        forecast = r.json()
        weather["forecast"] = list(map(parse_forecast, forecast["list"]))
        return weather
    except (requests.exceptions.RequestException, ValueError, KeyError) as e:
        logging.getLogger(__name__).error(f"Error fetching weather: {e}")
        return None
