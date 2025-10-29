import os
from datetime import datetime, timedelta
from typing import Optional

from binance import Client
from django.utils.timezone import make_aware

from charts import binance_tools, coinalyze_tools
from charts.binance_tools import binance_get_values
from charts.charts_constants import COINALYZE_EXCHANGE_CODES, COINALYZE_TRACKED_DATA
from charts.coinalyze_tools import coinalyze_get_values
from charts.misc import interval_to_timedelta, round_time
from charts.models import Exchange, Ticker, Chart
import logging

logger = logging.getLogger(__name__)

COINALYZE_FUTURES_BASE_ASSETS = os.environ.get("COINALYZE_FUTURES_BASE_ASSETS").split(',')


def add_coinalyze_exchanges() -> None:
    """Add exchanges known by Coinalyze"""
    for exchange in COINALYZE_EXCHANGE_CODES.values():
        Exchange.objects.update_or_create(name=exchange.lower())


def add_coinalyze_futures_markets_tickers() -> None:
    coinalyze_tickers = coinalyze_tools.get_futures_markets()
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


def add_coinalyze_tracked_data_tickers() -> None:
    coinalyze_tickers = Ticker.objects.filter(
        additional_info__source="coinalyze",
        kind="Futures",
    )
    new_tickers = []
    for ticker in coinalyze_tickers:
        if not ticker.additional_info["base_asset"] in COINALYZE_FUTURES_BASE_ASSETS:
            continue
        for tracked_data_type in COINALYZE_TRACKED_DATA:
            exchange = Exchange.objects.get(name=COINALYZE_EXCHANGE_CODES[ticker.additional_info["exchange"]].lower())
            new_tickers.append(
                Ticker(
                    exchange=exchange,
                    kind=tracked_data_type,
                    name=ticker.name,
                    additional_info=ticker.additional_info,
                )
            )
    Ticker.objects.bulk_create(new_tickers, ignore_conflicts=True)


#TODO: create tools for inserting historical data, especially funding rates with specificed intervals;
# rethink creating separate model for coinalyze future markets, and add a type
# (eg. market, funding_rate, open_interest) to Ticker to differentiate;
def update_values_coinalyze(
    ticker: str,
    interval: str = Client.KLINE_INTERVAL_1HOUR,
    date_start: Optional[datetime] = None,
    date_end: Optional[datetime] = None,
) -> None:
    logger.info(
        "Updating Futures values for ticker <%s>, interval <%s>",
        ticker,
        interval,
    )
    for tracked_data_type in COINALYZE_TRACKED_DATA:
        try:
            ticker_object = Ticker.objects.get(name=ticker, kind=tracked_data_type)
        except Exception:
            logger.error("Error during updating values for ticker <%s>, type <%s>!", ticker, tracked_data_type)
            return
        get_values_kwargs = {"ticker": ticker, "interval": interval, "data_type": tracked_data_type}
        if date_start:
            get_values_kwargs["from_"] = date_start
        if date_end:
            get_values_kwargs["to"] = date_end
        klines_iterator = coinalyze_get_values(**get_values_kwargs)
        chart_entries = (
            Chart(
                ticker=ticker_object,
                interval=interval_to_timedelta(interval),
                timestamp=make_aware(round_time(datetime.fromtimestamp(k.timestamp))),
                open=float(k.open),
                high=float(k.high),
                low=float(k.low),
                close=float(k.close),
                # volume is not nullable, but it's not applicable here
                # arguably better to have some explicit 0s, than relaxing that condition in DB
                volume=0,
            )
            for k in klines_iterator
        )
        Chart.objects.bulk_update_or_create(
            chart_entries,
            update_fields=["open", "high", "low", "close"],
            match_field=("ticker", "interval", "timestamp"),
        )
    logger.info(
        "Updating Coinalyze values for ticker <%s>, interval <%s>... DONE",
        ticker,
        interval,
    )
