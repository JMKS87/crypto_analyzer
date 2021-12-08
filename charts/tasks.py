from datetime import datetime
from typing import Iterable, Optional

from binance import Client
from celery import shared_task

from charts.binance_tasks import add_binance, add_binance_tickers, update_values


@shared_task
def populate_binance_tickers() -> None:
    add_binance()
    add_binance_tickers()


@shared_task
def _update_values(
    ticker: str,
    interval: str = Client.KLINE_INTERVAL_1DAY,
    date_start: Optional[datetime] = None,
    date_end: Optional[datetime] = None,
) -> None:
    update_values(ticker=ticker, interval=interval, date_start=date_start, date_end=date_end)


@shared_task
def update_binance_values(
    tickers: Iterable[str] = ("BTCUSDT", "ETHUSDT"),
    intervals: Optional[Iterable[str]] = (Client.KLINE_INTERVAL_1DAY,),
) -> None:
    for ticker in tickers:
        for interval in intervals:
            _update_values.delay(ticker=ticker, interval=interval)
