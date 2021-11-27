from celery import shared_task

from charts.binance_tasks import _add_binance, _add_binance_tickers, _update_values


@shared_task
def update_binance() -> None:
    _add_binance()
    _add_binance_tickers()
    _update_values()