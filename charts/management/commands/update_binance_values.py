import logging

from django.core.management import BaseCommand

from charts.tasks import populate_binance_tickers, update_binance_values

logger = logging.getLogger(__name__)

# make manage.py CMD=update_binance_values
class Command(BaseCommand):
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("--tickers", help="Tickers to update")
        parser.add_argument("--intervals", help="Intervals to update")

    def handle(self, *args, **kwargs):
        logging.getLogger().setLevel(logging.INFO)
        logger.info("Scheduling Binance update...")
        kwargs_for_job = {}
        if kwargs["tickers"]:
            kwargs_for_job["tickers"] = kwargs["tickers"].split(",")
        if kwargs["intervals"]:
            kwargs_for_job["intervals"] = kwargs["intervals"].split(",")
        update_binance_values.delay(**kwargs_for_job)
        logger.info("Scheduling Binance update... DONE")
