import requests
from datetime import datetime

BUS_STOP_SITE_ID = 2216
TRAIN_STOP_SITE_ID = 9633

BUS_STOP_WALK_MINUTES = 6
TRAIN_STOP_WALK_MINUTES = 10


def get_morning_departures(now):
    if not _is_morning_hours(now):
        return []

    bus_departures = _fetch_departures(BUS_STOP_SITE_ID)
    filtered_buses = [dep for dep in bus_departures if _is_expected_bus_departure(dep)]

    train_departures = _fetch_departures(TRAIN_STOP_SITE_ID)
    filtered_trains = [
        dep for dep in train_departures if _is_expected_train_departure(dep)
    ]

    all_departures = [
        _transform_departure(dep, BUS_STOP_WALK_MINUTES, now) for dep in filtered_buses
    ]
    all_departures.extend(
        [_transform_departure(dep, TRAIN_STOP_WALK_MINUTES, now) for dep in filtered_trains]
    )
    all_departures.sort(key=lambda d: d["scheduled_time"])

    return all_departures


def _is_morning_hours(now):
    return 7 <= now.hour < 11


def _is_expected_bus_departure(departure):
    line = departure.get("line", {})
    return (
        line.get("designation") == "605"
        and line.get("transport_mode") == "BUS"
        and departure.get("destination") == "Danderyds sjukhus"
    )


def _is_expected_train_departure(departure):
    line = departure.get("line", {})
    destination = departure.get("destination", "")
    return line.get("transport_mode") == "TRAM" and "Stockholms östra" in destination


def _fetch_departures(site_id):
    response = requests.get(f"https://transport.integration.sl.se/v1/sites/{site_id}/departures")
    data = response.json()
    return data.get("departures", [])


def _transform_departure(raw, walk_time_minutes, now):
    scheduled_str = raw["scheduled"]
    scheduled_time = datetime.fromisoformat(scheduled_str)

    time_until_departure = (scheduled_time - now).total_seconds() / 60
    is_missed = time_until_departure < walk_time_minutes

    return {
        "stop_name": raw["stop_area"]["name"],
        "destination": raw["destination"],
        "line_number": raw["line"]["designation"],
        "scheduled_time": scheduled_time,
        "transport_mode": raw["line"]["transport_mode"],
        "journey_state": raw["journey"]["state"],
        "walk_time_minutes": walk_time_minutes,
        "is_missed": is_missed,
    }
