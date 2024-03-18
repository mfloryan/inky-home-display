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
    query = '{ viewer { homes { currentSubscription { priceInfo{today {total startsAt}}}}}}'

    response_json = load_data_from_tibber(load_token(), query)
    hourly = response_json['data']['viewer']['homes'][0]['currentSubscription']['priceInfo']['today']
    return list(map(lambda _: _['total'], hourly))


def load_day_stats_from_tibber():
    query = \
        ("{ viewer { homes { "
         "consumption(resolution: HOURLY, last: 24) { nodes { from to cost consumption }}"
         "production(resolution: HOURLY, last: 24) { nodes { from to profit production }}"
         "}}}")

    data = load_data_from_tibber(load_token(), query)['data']['viewer']['homes'][0]

    now = datetime.now()
    today = lambda date: date.day == now.day

    stats = {
        'production': 0, 'profit': 0,
        'consumption': 0, 'cost': 0
    }

    for n in data['production']['nodes']:
        if today(datetime.fromisoformat(n['from'])):
            if n['production']: stats['production'] += n['production']
            if n['profit']: stats['profit'] += n['profit']

    consumption = {'consumption': 0, 'cost': 0}
    for n in data['consumption']['nodes']:
        if today(datetime.fromisoformat(n['from'])):
            if n['consumption']: stats['consumption'] += n['consumption']
            if n['cost']: stats['cost'] += n['cost']

    return stats


def load_data_from_tibber(token, query):
    response = requests.post(
        'https://api.tibber.com/v1-beta/gql',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        },
        json={'query': query})

    if response.status_code != 200:
        raise RuntimeError(
            f"Tiber responded with response code: {response.status_code}")

    response_json = response.json()
    if 'errors' in response_json:
        raise RuntimeError(
            f"Tibber returned errors: {response_json['errors']}")

    return response_json


def tibber_energy_prices():
    return cache(f"tibber-prices-{datetime.now().strftime('%Y%m%d')}", load_prices_from_tibber)


def tibber_energy_stats():
    return cache(f"tibber-stats-{datetime.now().strftime('%Y%m%d-%H')}", load_day_stats_from_tibber)
