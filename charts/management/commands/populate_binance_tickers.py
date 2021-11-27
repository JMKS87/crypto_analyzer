import logging
from charts import binance_tools

from django.conf import settings
from django.core.management import BaseCommand

from charts.models import Exchange, Ticker

logger = logging.getLogger(__name__)


def _add_binance() -> None:
    """Add Binance to Exchanges"""
    Exchange.objects.update_or_create(name='binance')




def _add_binance_tickers():
    tickers = binance_tools.get_tickers()
    exchange = Exchange.objects.get(name='binance')
    tickers_entries = (Ticker(exchange=exchange, name=ticker) for ticker in tickers)
    Ticker.objects.bulk_create(tickers_entries, ignore_conflicts=True)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        logging.getLogger().setLevel(logging.INFO)
        logger.info('Populating Binance tickers...')
        _add_binance()
        _add_binance_tickers()
        logger.info('Populating Binance tickers... DONE')
