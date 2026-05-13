from datetime import datetime
import requests
from config import load_token


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
        "appid": load_token("openweather-api-token", "Open Weather"),
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
        },
    }

    forecast_payload = payload | {"cnt": 8}  # Get next 24h
    r = requests.get(
        "https://api.openweathermap.org/data/2.5/forecast", params=forecast_payload, timeout=10
    )
    forecast = r.json()
    weather["forecast"] = list(map(parse_forecast, forecast["list"]))
    return weather
