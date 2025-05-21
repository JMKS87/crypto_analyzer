from datetime import datetime
from typing import Optional

from binance import Client
from django.utils.timezone import make_aware

from charts import binance_tools
from charts.binance_tools import get_values
from charts.misc import interval_to_timedelta, round_time
from charts.models import Exchange, Ticker, Chart
import logging

logger = logging.getLogger(__name__)

EXCHANGE_NAME = "binance"


def add_binance() -> None:
    """Add Binance to Exchanges"""
    Exchange.objects.update_or_create(name=EXCHANGE_NAME)


def add_binance_tickers() -> None:
    tickers = binance_tools.get_tickers()
    exchange = Exchange.objects.get(name=EXCHANGE_NAME)
    tickers_entries = (Ticker(exchange=exchange, name=ticker) for ticker in tickers)
    Ticker.objects.bulk_create(tickers_entries, ignore_conflicts=True)


def update_values(
    ticker: str,
    interval: str = Client.KLINE_INTERVAL_1DAY,
    date_start: Optional[datetime] = None,
    date_end: Optional[datetime] = None,
) -> None:
    logger.info(
        "Updating values for ticker <%s>, exchange <%s>, interval <%s>",
        ticker,
        EXCHANGE_NAME,
        interval,
    )
    exchange = Exchange.objects.get(name=EXCHANGE_NAME)
    try:
        ticker_object = Ticker.objects.get(exchange=exchange, name=ticker)
    except Exception:
        logger.error("Error during updating values for ticker <%s>!", ticker)
        return
    get_values_kwargs = {"ticker": ticker, "interval": interval}
    if date_start:
        get_values_kwargs["from_"] = date_start
    if date_end:
        get_values_kwargs["to"] = date_end
    klines_iterator = get_values(**get_values_kwargs)
    chart_entries = (
        Chart(
            ticker=ticker_object,
            interval=interval_to_timedelta(interval),
            timestamp=make_aware(round_time(datetime.fromtimestamp(k.open_time / 1000))),
            end_timestamp=make_aware(round_time(datetime.fromtimestamp(k.close_time / 1000))),
            open=float(k.open),
            high=float(k.high),
            low=float(k.low),
            close=float(k.close),
            volume=float(k.volume),
        )
        for k in klines_iterator
    )
    Chart.objects.bulk_update_or_create(
        chart_entries,
        update_fields=["open", "high", "low", "close", "volume"],
        match_field=("ticker", "interval", "timestamp"),
    )
    logger.info(
        "Updating values for ticker <%s>, exchange <%s>, interval <%s>... DONE",
        ticker,
        EXCHANGE_NAME,
        interval,
    )
    # WIP, still TODO
