import logging

import requests

from config import HOUSE_API_URL

SELECTED_SENSORS = [
    ("sensor-up", "Salon"),
    ("sensor-master-bedroom", "Sypialnia"),
    ("sensor-kitchen", "Kuchnia"),
]

logger = logging.getLogger(__name__)


def get_house_temperatures() -> list[dict] | None:
    try:
        response = requests.get(HOUSE_API_URL, timeout=5)
        response.raise_for_status()
        readings_by_name = {r["name"]: r for r in response.json()["readings"]}
        result = [
            {"label": label, "temp": readings_by_name[name]["temperature"]}
            for name, label in SELECTED_SENSORS
            if name in readings_by_name
        ]
        return result if result else None
    except Exception as e:
        logger.error("Failed to fetch house temperatures: %s", e)
        return None
