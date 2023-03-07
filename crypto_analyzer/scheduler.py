import logging
import os
import time
from typing import List

import django
import schedule

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crypto_analyzer.settings")
django.setup()

from charts.tasks import update_binance_values

logger = logging.getLogger(__name__)

TICKERS_UPDATE_1M: List[str] = os.environ.get("TICKERS_UPDATE_1M", "").split(",")


def update_binance_tickers_1m():
    update_binance_values.delay(intervals=['1m'], tickers=TICKERS_UPDATE_1M)


def run():
    logger.info("Scheduler process has started.")
    schedule.every(1).minute.do(update_binance_tickers_1m)
    while True:
        schedule.run_pending()
        time.sleep(15)


if __name__ == "__main__":
    run()
