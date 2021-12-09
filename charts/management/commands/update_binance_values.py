import logging

from django.core.management import BaseCommand

from charts.models import Ticker, Exchange
from charts.tasks import populate_binance_tickers, update_binance_values

logger = logging.getLogger(__name__)

EXCHANGE_NAME = "binance"

# make manage.py CMD="update_binance_values --tickers=all"
class Command(BaseCommand):
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("--tickers", help="Tickers to update")
        parser.add_argument("--intervals", help="Intervals to update")

    def handle(self, *args, **kwargs):
        logging.getLogger().setLevel(logging.INFO)
        logger.info("Scheduling Binance update...")
        kwargs_for_job = {}
        if tickers := kwargs["tickers"]:
            if tickers == "all":
                exchange = Exchange.objects.get(name=EXCHANGE_NAME)
                tickers_objects = Ticker.objects.filter(exchange=exchange).order_by("name")
                tickers = [t.name for t in tickers_objects]
            else:
                tickers = tickers.split(",")
            kwargs_for_job["tickers"] = tickers
        if kwargs["intervals"]:
            kwargs_for_job["intervals"] = kwargs["intervals"].split(",")
        update_binance_values.delay(**kwargs_for_job)
        logger.info("Scheduling Binance update... DONE")
