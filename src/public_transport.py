import requests
from datetime import datetime

SITE_ID = 2216


def get_morning_departures(now):
    if not _is_morning_hours(now):
        return []

    raw_departures = _fetch_departures()
    filtered = [dep for dep in raw_departures if _is_expected_bus_departure(dep)]
    return [_transform_departure(dep) for dep in filtered]


def _is_morning_hours(now):
    return 7 <= now.hour < 11


def _is_expected_bus_departure(departure):
    line = departure.get("line", {})
    return (
        line.get("designation") == "605"
        and line.get("transport_mode") == "BUS"
        and departure.get("destination") == "Danderyds sjukhus"
    )


def _fetch_departures():
    response = requests.get(f"https://transport.integration.sl.se/v1/sites/{SITE_ID}/departures")
    data = response.json()
    return data.get("departures", [])


def _transform_departure(raw):
    scheduled_str = raw["scheduled"]
    scheduled_time = datetime.fromisoformat(scheduled_str)

    return {
        "destination": raw["destination"],
        "line_number": raw["line"]["designation"],
        "scheduled_time": scheduled_time,
        "transport_mode": raw["line"]["transport_mode"],
        "journey_state": raw["journey"]["state"],
    }
