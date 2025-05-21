import os
from typing import Iterable

import requests

API_KEY = os.environ.get("COINALYZE_API_KEY")
HEADERS = {"api_key": API_KEY}

def get_echanges():
    response = requests.get("https://api.coinalyze.net/v1/exchanges", headers=HEADERS)
    js = response.json()
    print('a')

def get_futures_markets():
    response = requests.get("https://api.coinalyze.net/v1/future-markets", headers=HEADERS)
    js = response.json()
    binance_symbols = []
    for el in js:
        if el['base_asset'] == 'BTC' and el["exchange"] == "A":
            binance_symbols.append(el['symbol'])
            print(el)
    print('a')
    return binance_symbols

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
