import os
from typing import Iterable

import requests

API_KEY_LOCATION = os.path.join("secrets", os.environ.get("COINALYZE_API_KEY_LOCATION"))
with open(API_KEY_LOCATION, "r") as inf:
    API_KEY = inf.read().strip()
HEADERS = {"api_key": API_KEY}

def get_echanges():
    response = requests.get("https://api.coinalyze.net/v1/exchanges", headers=HEADERS)
    js = response.json()
    print('a')


def get_futures_markets():
    response = requests.get("https://api.coinalyze.net/v1/future-markets", headers=HEADERS)
    js = response.json()
    markets = []
    for el in js:
        markets.append(el)
    return markets

def get_predicted_funding_rate_history(symbols: Iterable):
    params = {
        "symbols": ",".join(symbols),
        "interval": "1hour",
        "from": 743467806,
        "to": 1744253538,
        # "to": 1744253295903,
    }
    response = requests.get('https://api.coinalyze.net/v1/predicted-funding-rate-history', headers=HEADERS, params=params)
    js = response.json()
    print('a')


def get_current_predicted_funding_rate(binance_symbols):
    response = requests.get('https://api.coinalyze.net/v1/predicted-funding-rate', headers=HEADERS,
                            params={"symbols": ",".join(binance_symbols)},
                            )
    js = response.json()
    print('a')


if __name__ == "__main__":
    get_echanges()
    binance_symbols = get_futures_markets()
    get_predicted_funding_rate_history(binance_symbols)
    # get_current_predicted_funding_rate(binance_symbols)
