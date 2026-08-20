import logging
import os
import time
from typing import List

import django
import schedule

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crypto_analyzer.settings")
django.setup()

from charts.tasks import update_binance_values, update_coinalyze_values

logger = logging.getLogger(__name__)

LOCAL_UPDATE = os.environ.get("LOCAL_UPDATE", "False").lower() == "true"
TICKERS_UPDATE_1M: List[str] = os.environ.get("TICKERS_UPDATE_1M", "").split(",")
TICKERS_UPDATE_1H: List[str] = os.environ.get("TICKERS_UPDATE_1H", "").split(",")
COINALYZE_UPDATE_1H: List[str] = os.environ.get("COINALYZE_UPDATING_FUTURES_1H_BASE_ASSETS", "").split(",")


def update_binance_tickers_1m():
    if not LOCAL_UPDATE:
        return
    update_binance_values.delay(intervals=['1m'], tickers=TICKERS_UPDATE_1M)
    logger.info("Scheduled updating Binance 1m, tickers <%s>", TICKERS_UPDATE_1M)


def update_binance_tickers_1h():
    if not LOCAL_UPDATE:
        return
    update_binance_values.delay(intervals=['1h'], tickers=TICKERS_UPDATE_1H)
    logger.info("Scheduled updating Binance 1h, tickers <%s>", TICKERS_UPDATE_1H)


def update_coinalyze_futures_1h():
    if not LOCAL_UPDATE:
        return
    update_coinalyze_values.delay(intervals=['1h'], tickers=COINALYZE_UPDATE_1H)
    logger.info("Scheduled updating Coinalyze 1h, tickers <%s>",  COINALYZE_UPDATE_1H)


def run():
    logger.info("Scheduler process has started.")
    schedule.every(1).minute.do(update_binance_tickers_1m)
    schedule.every(10).minutes.do(update_binance_tickers_1h)
    # TODO: investigate later
    #schedule.every(30).minutes.do(update_coinalyze_futures_1h)
    schedule.run_all(delay_seconds=20)
    while True:
        schedule.run_pending()
        time.sleep(15)

if __name__ == "__main__":
    run()
