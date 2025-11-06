import requests
from datetime import datetime, timedelta
from cache import cache


LAHALLSVIADUKTEN_SITE_ID = 2216
ROSLAGS_NASBY_SITE_ID = 9633

LAHALLSVIADUKTEN_WALK_MINUTES = 6
ROSLAGS_NASBY_WALK_MINUTES = 10


def get_morning_departures_cached():
    """
    Cached wrapper for get_morning_departures with 15-minute expiration.
    Cache key is rounded to nearest 15-minute interval (00, 15, 30, 45).
    """
    now = datetime.now()
    rounded_minute = (now.minute // 15) * 15
    cache_key = f"sl-departures-{now.strftime('%Y%m%d-%H')}{rounded_minute:02d}"

    def fetch_and_serialize():
        departures = get_morning_departures()
        return [
            {
                **dep,
                "scheduled_time": dep["scheduled_time"].isoformat()
            }
            for dep in departures
        ]

    cached_data = cache(cache_key, fetch_and_serialize)

    return [
        {
            **dep,
            "scheduled_time": datetime.fromisoformat(dep["scheduled_time"])
        }
        for dep in cached_data
    ]


def get_morning_departures():
    """
    Get morning commute departures (7am-11am) from two stops:
    - Lahällsviadukten: bus 605 towards Danderyds sjukhus
    - Roslags Näsby: all trains towards Stockholms östra

    Returns a flat list of departures with stop info, sorted by scheduled time.
    Each departure includes is_missed flag based on walk time.
    Shows at least 1 departure, or all departures within 30 minutes.
    """
    current_hour = datetime.now().hour

    if not (7 <= current_hour < 11):
        return []

    departures = []

    lahalls_deps = _fetch_departures_from_site(LAHALLSVIADUKTEN_SITE_ID)
    departures.extend(
        _filter_lahallsviadukten_departures(lahalls_deps, LAHALLSVIADUKTEN_WALK_MINUTES)
    )

    nasby_deps = _fetch_departures_from_site(ROSLAGS_NASBY_SITE_ID)
    departures.extend(
        _filter_roslags_nasby_departures(nasby_deps, ROSLAGS_NASBY_WALK_MINUTES)
    )

    departures.sort(key=lambda d: d["scheduled_time"])

    return _apply_time_window_filter(departures)


def _fetch_departures_from_site(site_id):
    """Fetch raw departures from OpenSL API for a given site ID"""
    url = f"https://transport.integration.sl.se/v1/sites/{site_id}/departures"

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()
    return data.get("departures", [])


def _filter_lahallsviadukten_departures(raw_departures, walk_minutes):
    """
    Filter for bus 605 towards Danderyds sjukhus from Lahällsviadukten
    """
    filtered = []
    now = datetime.now()

    for dep in raw_departures:
        line_number = dep.get("line", {}).get("designation")
        destination = dep.get("destination")

        if line_number == "605" and destination == "Danderyds sjukhus":
            scheduled_time = datetime.fromisoformat(dep["scheduled"])
            minutes_until = (scheduled_time - now).total_seconds() / 60

            filtered.append({
                "stop_name": "Lahällsviadukten",
                "line_number": line_number,
                "destination": destination,
                "scheduled_time": scheduled_time,
                "walk_time_minutes": walk_minutes,
                "is_missed": minutes_until < walk_minutes
            })

    return filtered


def _filter_roslags_nasby_departures(raw_departures, walk_minutes):
    """
    Filter for all trains towards Stockholms östra from Roslags Näsby
    """
    filtered = []
    now = datetime.now()

    for dep in raw_departures:
        transport_mode = dep.get("line", {}).get("transport_mode")
        direction = dep.get("direction")

        if transport_mode == "TRAM" and direction == "Stockholms östra":
            line_number = dep.get("line", {}).get("designation")
            scheduled_time = datetime.fromisoformat(dep["scheduled"])
            minutes_until = (scheduled_time - now).total_seconds() / 60

            filtered.append({
                "stop_name": "Roslags Näsby",
                "line_number": line_number,
                "destination": direction,
                "scheduled_time": scheduled_time,
                "walk_time_minutes": walk_minutes,
                "is_missed": minutes_until < walk_minutes
            })

    return filtered


def _apply_time_window_filter(departures):
    """
    Show at least 1 departure, or all departures within 30 minutes
    """
    if not departures:
        return []

    now = datetime.now()
    cutoff_time = now + timedelta(minutes=30)

    within_window = [
        d for d in departures
        if d["scheduled_time"] <= cutoff_time
    ]

    if within_window:
        return within_window
    else:
        return [departures[0]]
