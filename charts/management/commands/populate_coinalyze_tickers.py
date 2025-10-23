import logging

from django.core.management import BaseCommand

from charts.tasks import populate_coinalyze_tickers

logger = logging.getLogger(__name__)

# make manage.py CMD=populate_coinalyze_tickers
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        logging.getLogger().setLevel(logging.INFO)
        logger.info("Populating Coinalyze tickers...")
        populate_coinalyze_tickers.delay()
        logger.info("Populating Coinalyze tickers... DONE")
