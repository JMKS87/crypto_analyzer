import os
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from typing import List

from binance import Client

API_KEY = os.environ.get("BINANCE_API_KEY")
API_SECRET = os.environ.get("BINANCE_API_SECRET")


@dataclass
class KlineData:
    open_time: int
    open: str
    high: str
    low: str
    close: str
    volume: str
    close_time: int
    quote_asset_volume: str
    number_of_trader: int
    taker_buy_base_asset_volume: str
    taker_buy_quote_asset_volume: str
    ignore: str

    @classmethod
    def from_list(cls, l: List) -> "KlineData":
        return cls(
            open_time=l[0],
            open=l[1],
            high=l[2],
            low=l[3],
            close=l[4],
            volume=l[5],
            close_time=l[6],
            quote_asset_volume=l[7],
            number_of_trader=l[8],
            taker_buy_base_asset_volume=l[9],
            taker_buy_quote_asset_volume=l[10],
            ignore=l[11],
        )


@lru_cache(maxsize=1)
def _get_client() -> Client:
    client = Client(API_KEY, API_SECRET)
    return client


def get_tickers():
    client = _get_client()
    tickers = client.get_all_tickers()
    # TODO
    values = [row["symbol"] for row in tickers]
    return values


def get_values(ticker: str, interval: int, from_: datetime, to: datetime) -> List:
    klines = _get_client().get_historical_klines(
        "BTCUSDT", Client.KLINE_INTERVAL_1MINUTE, "1 Dec, 2017", "2 Dec, 2017"
    )
    print("a")


if __name__ == "__main__":
    get_tickers()
    # get_values(1, 2, 3, 4)

# TODO: CRON-compatible filling of historical data
