import os
from datetime import datetime, timedelta
from typing import Optional

from binance import Client
from django.utils.timezone import make_aware

from charts import binance_tools, coinalyze_api
from charts.binance_tools import get_values
from charts.charts_constants import COINALYZE_EXCHANGE_CODES
from charts.misc import interval_to_timedelta
from charts.models import Exchange, Ticker, Chart
import logging

logger = logging.getLogger(__name__)

COINALYZE_FUTURES_BASE_ASSETS = os.environ.get("COINALYZE_FUTURES_BASE_ASSETS").split(',')


def add_coinalyze_exchanges() -> None:
    """Add exchanges known by Coinalyze"""
    for exchange in COINALYZE_EXCHANGE_CODES.values():
        Exchange.objects.update_or_create(name=exchange.lower())


def add_coinalyze_futures_markets_tickers() -> None:
    coinalyze_tickers = coinalyze_api.get_futures_markets()
    new_tickers = []
    for ticker in coinalyze_tickers:
        if not ticker["base_asset"] in COINALYZE_FUTURES_BASE_ASSETS:
            continue
        exchange = Exchange.objects.get(name=COINALYZE_EXCHANGE_CODES[ticker["exchange"]].lower())
        ticker["source"] = "coinalyze"
        new_tickers.append(
            Ticker(
                exchange=exchange,
                kind="Futures",
                name=ticker["symbol"],
                additional_info=ticker,
            )
        )
    Ticker.objects.bulk_create(new_tickers, ignore_conflicts=True)


#TODO: create tools for inserting historical data, especially funding rates with specificed intervals;
# rethink creating separate model for coinalyze future markets, and add a type
# (eg. market, funding_rate, open_interest) to Ticker to differentiate;
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
