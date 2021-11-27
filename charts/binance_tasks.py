from charts import binance_tools
from charts.models import Exchange, Ticker


def _add_binance() -> None:
    """Add Binance to Exchanges"""
    Exchange.objects.update_or_create(name="binance")


def _add_binance_tickers() -> None:
    tickers = binance_tools.get_tickers()
    exchange = Exchange.objects.get(name="binance")
    tickers_entries = (Ticker(exchange=exchange, name=ticker) for ticker in tickers)
    Ticker.objects.bulk_create(tickers_entries, ignore_conflicts=True)


def _update_values() -> None:
    # TODO
    pass
