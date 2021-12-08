from celery import shared_task

from charts.binance_tasks import add_binance, add_binance_tickers, update_values


@shared_task
def update_binance() -> None:
    add_binance()
    add_binance_tickers()
    # update_values()
