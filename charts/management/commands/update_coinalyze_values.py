import logging

from django.core.management import BaseCommand

from charts.models import Ticker, Exchange
from charts.tasks import populate_binance_tickers, update_binance_values, update_coinalyze_values

logger = logging.getLogger(__name__)

# make manage.py CMD="update_coinalyze_values --base_assets=BTC --intervals=1h"
class Command(BaseCommand):
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("--base_assets", help="Base assets to update")
        parser.add_argument("--intervals", help="Intervals to update")

    def handle(self, *args, **kwargs):
        logging.getLogger().setLevel(logging.INFO)
        logger.info("Scheduling Coinalyze update...")
        kwargs_for_job = {}
        if base_assets := kwargs["base_assets"]:
            if base_assets == "all":
                tickers_objects = Ticker.objects.filter(
                    additional_info__source="coinalyze",
                    kind="Futures",
                )
                base_assets = {t.additional_info["base_asset"] for t in tickers_objects}
            else:
                base_assets = base_assets.split(",")
            kwargs_for_job["base_assets"] = base_assets
        if kwargs["intervals"]:
            kwargs_for_job["intervals"] = kwargs["intervals"].split(",")
        update_coinalyze_values.delay(**kwargs_for_job)
        logger.info("Scheduling Coinalyze update... DONE")
