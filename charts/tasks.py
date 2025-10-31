import os

import pytz

from datetime import datetime, timedelta
from typing import Iterable, Optional, Tuple, List, Set

from binance import Client
from celery import shared_task
from django.utils import timezone

from charts.binance_tasks import add_binance, add_binance_tickers, update_values_binance
from charts.charts_constants import DEFAULT_KLINES_TO_FETCH, BINANCE_START_TIME, COINALYZE_START_TIME, \
    COINALYZE_EXCHANGE_CODES
from charts.coinalyze_tasks import add_coinalyze_exchanges, add_coinalyze_futures_markets_tickers, \
    update_values_coinalyze, add_coinalyze_tracked_data_tickers
from charts.misc import interval_to_timedelta
from charts.models import ChartLastUpdated, Exchange, Ticker

COINALYZE_TRACKED_EXCHANGES: List[str] = os.environ.get("COINALYZE_TRACKED_EXCHANGES", "").split(",")

utc=pytz.UTC

def _get_coinalyze_tracked_exchanges_codes() -> Set[str]:
    tracked_exchange_codes = set()
    for code, exchange_name in COINALYZE_EXCHANGE_CODES.items():
        if exchange_name.lower() in COINALYZE_TRACKED_EXCHANGES:
            tracked_exchange_codes.add(code)
    return tracked_exchange_codes


@shared_task
def populate_binance_tickers() -> None:
    add_binance()
    add_binance_tickers()


@shared_task
def populate_coinalyze_tickers() -> None:
    add_coinalyze_exchanges()
    add_coinalyze_futures_markets_tickers()
    add_coinalyze_tracked_data_tickers()


def _determine_dates_to_update_binance(ticker: str, interval: str, exchange: str = "binance") -> Tuple[datetime, datetime, ChartLastUpdated]:
    #TODO: think about merging this with _determine_dates_to_update_coinalyze
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


def _determine_dates_to_update_coinalyze(ticker: str, interval: str) -> Tuple[datetime, datetime, ChartLastUpdated]:
    #TODO: think about merging this with _determine_dates_to_update_binance
    ticker_object = Ticker.objects.get(name=ticker, kind="Futures")
    interval_timedelta = interval_to_timedelta(interval)
    chart_last_updated, created = ChartLastUpdated.objects.get_or_create(
        ticker=ticker_object,
        interval=interval_timedelta,
        defaults={"last_updated": COINALYZE_START_TIME},
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
def _update_spot_values(
    ticker: str,
    interval: str = Client.KLINE_INTERVAL_1DAY,
    date_start: Optional[datetime] = None,
    date_end: Optional[datetime] = None,
) -> None:
    chart_last_updated = None
    if not date_start:
        date_start, date_end, chart_last_updated = _determine_dates_to_update_binance(ticker, interval)
    update_values_binance(ticker=ticker, interval=interval, date_start=date_start, date_end=date_end)
    # truthy chart_last_updated indicates it was invoked without date_start, ie. recurring
    if chart_last_updated:
        chart_last_updated.save()




@shared_task
def _update_coinalyze_values(
    ticker: str,
    interval: str = Client.KLINE_INTERVAL_1HOUR,
    date_start: Optional[datetime] = None,
    date_end: Optional[datetime] = None,
) -> None:
    chart_last_updated = None
    if not date_start:
        date_start, date_end, chart_last_updated = _determine_dates_to_update_coinalyze(ticker, interval)
    update_values_coinalyze(ticker=ticker, interval=interval, date_start=date_start, date_end=date_end)
    # truthy chart_last_updated indicates it was invoked without date_start, ie. recurring
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
            _update_spot_values.delay(
                ticker=ticker,
                interval=interval,
                date_start=date_start,
                date_end=date_end,
            )


@shared_task
def update_coinalyze_values(
    base_assets: Iterable[str] = ("BTC",),
    intervals: Optional[Iterable[str]] = (Client.KLINE_INTERVAL_1HOUR,),
    date_start: Optional[datetime] = None,
    date_end: Optional[datetime] = None,
) -> None:
    tracked_exchange_codes = _get_coinalyze_tracked_exchanges_codes()
    tickers_objects = Ticker.objects.filter(
        additional_info__base_asset__in=base_assets,
        additional_info__exchange__in=tracked_exchange_codes,
        additional_info__source="coinalyze",
        kind="Futures",
    )
    for ticker_object in tickers_objects:
        for interval in intervals:
            _update_coinalyze_values.delay(
                ticker=ticker_object.name,
                interval=interval,
                date_start=date_start,
                date_end=date_end,
            )
