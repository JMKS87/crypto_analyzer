import logging

from django.core.management import BaseCommand

from charts.tasks import update_binance

logger = logging.getLogger(__name__)

# make manage.py CMD=populate_binance_tickers
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        logging.getLogger().setLevel(logging.INFO)
        logger.info("Populating Binance tickers...")
        update_binance.delay()
        logger.info("Populating Binance tickers... DONE")
