import pytz

from datetime import datetime, timedelta
from typing import Iterable, Optional, Tuple

from binance import Client
from celery import shared_task
from django.utils import timezone

from charts.binance_tasks import add_binance, add_binance_tickers, update_values
from charts.charts_constants import DEFAULT_KLINES_TO_FETCH, BINANCE_START_TIME
from charts.misc import interval_to_timedelta
from charts.models import ChartLastUpdated, Exchange, Ticker

utc=pytz.UTC

@shared_task
def populate_binance_tickers() -> None:
    add_binance()
    add_binance_tickers()


def _determine_dates_to_update(ticker: str, interval: str, exchange: str = "binance") -> Tuple[datetime, datetime, ChartLastUpdated]:
    exchange_object = Exchange.objects.get(name=exchange)
    ticker_object = Ticker.objects.get(exchange=exchange_object, name=ticker)
    interval_timedelta = interval_to_timedelta(interval)
    chart_last_updated, created = ChartLastUpdated.objects.get_or_create(
        ticker=ticker_object,
        interval=interval_timedelta,
        defaults={"last_updated": BINANCE_START_TIME},
    )
    datetime_from = chart_last_updated.last_updated - 2 * interval_timedelta
    datetime_to = datetime_from + DEFAULT_KLINES_TO_FETCH * interval_timedelta
    datetime_to = min(
        datetime_to.replace(tzinfo=utc),
        datetime.now().replace(tzinfo=utc),
    )
    chart_last_updated.last_updated = datetime_to
    return datetime_from, datetime_to, chart_last_updated


@shared_task
def _update_values(
    ticker: str,
    interval: str = Client.KLINE_INTERVAL_1DAY,
    date_start: Optional[datetime] = None,
    date_end: Optional[datetime] = None,
) -> None:
    chart_last_updated = None
    if not date_start:
        date_start, date_end, chart_last_updated = _determine_dates_to_update(ticker, interval)
    update_values(ticker=ticker, interval=interval, date_start=date_start, date_end=date_end)
    if chart_last_updated:
        chart_last_updated.save()




@shared_task
def update_binance_values(
    tickers: Iterable[str] = ("BTCUSDT", "ETHUSDT"),
    intervals: Optional[Iterable[str]] = (Client.KLINE_INTERVAL_1DAY,),
    date_start: Optional[datetime] = None,
    date_end: Optional[datetime] = None,
) -> None:
    for ticker in tickers:
        for interval in intervals:
            _update_values.delay(
                ticker=ticker,
                interval=interval,
                date_start=date_start,
                date_end=date_end,
            )
