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


def _fetch_from_api(url, params):
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.JSONDecodeError as ex:
        logging.getLogger(__name__).error("Malformed JSON response from OpenWeather API")
        raise RuntimeError("Invalid JSON response") from ex
    except requests.exceptions.RequestException as ex:
        logging.getLogger(__name__).error("Error fetching data from OpenWeather API")
        raise RuntimeError("API request failed") from ex


def get_weather():
    def parse_forecast(item):
        return {
            "time": datetime.fromtimestamp(item["dt"]),
            "temp": item["main"]["temp"],
            "weather": item["weather"][0]["description"],
        }

    payload = {
        "lat": "59.4308",
        "lon": "18.0637",
        "units": "metric",
        "lang": "pl",
        "appid": load_token(),
    }

    current_weather = _fetch_from_api(
        "https://api.openweathermap.org/data/2.5/weather", params=payload
    )
    weather = {
        "name": current_weather["name"],
        "sunrise": datetime.fromtimestamp(current_weather["sys"]["sunrise"]),
        "sunset": datetime.fromtimestamp(current_weather["sys"]["sunset"]),
        "now": {
            "temp": current_weather["main"]["temp"],
        },
    }

    forecast_payload = payload | {"cnt": 8}  # Get next 24h
    forecast = _fetch_from_api(
        "https://api.openweathermap.org/data/2.5/forecast", params=forecast_payload
    )
    weather["forecast"] = [parse_forecast(item) for item in forecast["list"]]
    return weather
