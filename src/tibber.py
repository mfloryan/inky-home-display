import functools
import json
import logging
from datetime import datetime

import requests

from cache import cache
from tokens import read_token_file

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=1)
def load_token():
    return read_token_file("tibber-api-token", "Unable to load Tibber token")


def load_prices_from_tibber():
    query = (
        "{ viewer { homes { currentSubscription { priceInfo(resolution:QUARTER_HOURLY){today {total startsAt}}}}}}"
    )

    response_json = load_data_from_tibber(load_token(), query)

    homes = response_json.get("data", {}).get("viewer", {}).get("homes", [])
    if not homes:
        logger.debug("Tibber prices response: %s", json.dumps(response_json))
        raise RuntimeError("No homes found in Tibber API response")

    home = next((h for h in homes if h.get("currentSubscription") is not None), None)
    if home is None:
        logger.debug("Tibber prices response: %s", json.dumps(response_json))
        raise RuntimeError(
            "No active subscription found in Tibber API response. "
            "Please check your Tibber account status."
        )

    current_subscription = home.get("currentSubscription")

    price_info = current_subscription.get("priceInfo")
    if price_info is None:
        logger.debug("Tibber prices response: %s", json.dumps(response_json))
        raise RuntimeError("No price information available in Tibber API response")

    today_prices = price_info.get("today")
    if today_prices is None:
        logger.debug("Tibber prices response: %s", json.dumps(response_json))
        raise RuntimeError("No prices available for today in Tibber API response")

    return list(map(lambda _: _["total"], today_prices))


def load_day_stats_from_tibber():
    query = (
        "{ viewer { homes { "
        "consumption(resolution: HOURLY, last: 24) { nodes { from to cost consumption }}"
        "production(resolution: HOURLY, last: 24) { nodes { from to profit production }}"
        "}}}"
    )

    response_json = load_data_from_tibber(load_token(), query)

    homes = response_json.get("data", {}).get("viewer", {}).get("homes", [])
    if not homes:
        logger.debug("Tibber stats response: %s", json.dumps(response_json))
        raise RuntimeError("No homes found in Tibber API response")

    data = next(
        (h for h in homes if h.get("consumption") is not None or h.get("production") is not None),
        None,
    )
    if data is None:
        logger.debug("Tibber stats response: %s", json.dumps(response_json))
        raise RuntimeError("No energy data found in Tibber API response")

    now = datetime.now()
    def today(date):
        return date.day == now.day

    stats = {"production": 0, "profit": 0, "consumption": 0, "cost": 0}

    production_data = data.get("production", {})
    production_nodes = production_data.get("nodes", [])
    for n in production_nodes:
        if today(datetime.fromisoformat(n["from"])):
            if n["production"]:
                stats["production"] += n["production"]
            if n["profit"]:
                stats["profit"] += n["profit"]

    consumption_data = data.get("consumption", {})
    consumption_nodes = consumption_data.get("nodes", [])
    for n in consumption_nodes:
        if today(datetime.fromisoformat(n["from"])):
            if n["consumption"]:
                stats["consumption"] += n["consumption"]
            if n["cost"]:
                stats["cost"] += n["cost"]

    return stats


def load_data_from_tibber(token, query):
    response = requests.post(
        "https://api.tibber.com/v1-beta/gql",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        json={"query": query},
    timeout=10)

    if response.status_code != 200:
        logger.debug("Tibber response body: %s", response.text)
        raise RuntimeError(
            f"Tibber responded with status {response.status_code}"
        )

    response_json = response.json()
    if "errors" in response_json:
        logger.debug("Tibber response: %s", json.dumps(response_json))
        raise RuntimeError(f"Tibber returned errors: {response_json['errors']}")

    return response_json


def tibber_energy_prices():
    return cache(
        f"tibber-prices-{datetime.now().strftime('%Y%m%d')}", load_prices_from_tibber
    )


def tibber_energy_stats():
    return cache(
        f"tibber-stats-{datetime.now().strftime('%Y%m%d-%H')}",
        load_day_stats_from_tibber,
    )
