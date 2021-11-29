import os
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from typing import List, Iterator, Union
import logging

from binance import Client

from charts.misc import timing

logger = logging.getLogger(__name__)

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


def get_tickers() -> List[str]:
    client = _get_client()
    response = client.get_all_tickers()
    tickers = [row["symbol"] for row in response]
    return tickers


@timing
def get_values(ticker: str, interval: str = Client.KLINE_INTERVAL_1DAY, from_: Union[datetime, str] = "17 Sep, 2017", to: Union[datetime, str] = "1 Jan, 2100") -> Iterator[KlineData]:
    # TODO: maybe internal chunking by date of API requests
    klines = _get_client().get_historical_klines(
        "BTCUSDT",
        interval,
        from_,
        to,
    )
    for kline in klines:
        yield KlineData.from_list(kline)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # get_tickers()
    list(get_values("BTCUSDT"))

# TODO: CRON-compatible filling of historical data, with granulation and possibly chunking into smaller fragments
