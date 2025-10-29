"""
Quota: 40 API calls/minute (per key).
When requesting eg. FundingRate for multiple symbols (tickers) at a time,
despite it being a single comma separated string,
each symbol counts as 1 API call, meaning one can exceed quota during
single request, disabling API for a whole minute.
#TODO: handle backoff
"""

import os
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Iterator, List, Union, Dict

import requests

from charts.charts_constants import COINALYZE_START_TIME

API_KEY_LOCATION = os.path.join("secrets", os.environ.get("COINALYZE_API_KEY_LOCATION"))
with open(API_KEY_LOCATION, "r") as inf:
    API_KEY = inf.read().strip()
HEADERS = {"api_key": API_KEY}

@dataclass
class CoinalyzeKline:
    open: str
    high: str
    low: str
    close: str
    timestamp: int

    @classmethod
    def from_dict(cls, d: Dict) -> "CoinalyzeKline":
        return cls(
            open=d["o"],
            high=d["h"],
            low=d["l"],
            close=d["c"],
            timestamp=d["t"],
        )


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
        "from": int(COINALYZE_START_TIME.timestamp()),
        "to": int(time.time()),
        # "to": 1744253295903,
    }
    response = requests.get('https://api.coinalyze.net/v1/predicted-funding-rate-history', headers=HEADERS, params=params)
    js = response.json()
    print('a')


def get_predicted_funding_rate_history_single(
        symbol: str,
        interval: str = "1hour",
) -> List[Dict]:
    #TODO: revert & handle properly
    interval = "1hour"
    params = {
        "symbols": symbol,
        "interval": interval,
        "from": int(COINALYZE_START_TIME.timestamp()),
        "to": int(time.time()),
    }
    response = requests.get('https://api.coinalyze.net/v1/predicted-funding-rate-history', headers=HEADERS, params=params)
    js = response.json()
    return js[0]["history"]


def get_predicted_funding_rate_history_try(symbols: Iterable = []):
    params = {
        "symbols": 'BTCUSD_PERP.A',
        "interval": "1hour",
        "from": int(time.time() - 24 * 60 * 60),
        "to": int(time.time()),
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


def coinalyze_get_values(
    ticker: str,
    #TODO: add data_type handling
    data_type: str,
    interval: str,
    from_: Union[datetime, int] = None,
    to: Union[datetime, int] = None,
) -> Iterator[CoinalyzeKline]:
    if data_type != "PredictedFundingRate":
        exit(1)
    # TODO: handle datetime to int
    if isinstance(from_, datetime):
        from_ = from_.strftime("%Y-%m-%d %H:%M")
    if isinstance(to, datetime):
        to = to.strftime("%Y-%m-%d %H:%M")
    klines = get_predicted_funding_rate_history_single(ticker, interval)#, interval)
    for kline in klines:
        yield CoinalyzeKline.from_dict(kline)



if __name__ == "__main__":
    # get_echanges()
    coinalyze_symbols = get_futures_markets()
    btc_tickers = [s["symbol"] for s in coinalyze_symbols if (s["base_asset"] == "BTC" and s["symbol"].endswith(".A"))]
    print(len(btc_tickers))
    get_predicted_funding_rate_history_single('BTCUSD_PERP.A')
    # get_current_predicted_funding_rate(binance_symbols)
    # get_predicted_funding_rate_history_try()
