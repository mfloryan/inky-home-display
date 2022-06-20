import logging
import os
from datetime import datetime
import requests
from cache import cache

def load_token():
    try:
        file = open(
            os.path.join(os.path.dirname(__file__), 'tibber-api-token'),
            'r',
            encoding="utf-8")
    except FileNotFoundError as ex:
        logging.getLogger(__name__).error("Token file `tibber-api-token` not found")
        raise RuntimeError("Unable to load Tibber token") from ex
    else:
        with file:
            return file.read()

def load_prices_from_tibber():
    query = {
        'query': '{ viewer { homes { currentSubscription { priceInfo{today {total startsAt}}}}}}'}
    headers = {'authorization': 'Bearer ' + load_token()}
    response = requests.post(
        'https://api.tibber.com/v1-beta/gql', json=query, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(
            f"Tiber responded with response code: {response.status_code}")

    response_json = response.json()
    if 'errors' in response_json:
        raise RuntimeError(
            f"Tibber returned errors: {response_json['errors']}")

    hourly = response_json['data']['viewer']['homes'][0]['currentSubscription']['priceInfo']['today']
    return list(map(lambda _: _['total'], hourly))

def tibber_energy_prices():
    return cache(f"tibber-{datetime.now().strftime('%Y%m%d')}", load_prices_from_tibber)
