import logging
import time

import schedule

logger = logging.getLogger(__name__)


def scheduled_function():
    print('Scheduler working')
    #TODO fill with some jobs, eg. updating some tickers regularly
    pass


def run():
    logger.info("Scheduler process has started.")
    schedule.every(1).minute.do(scheduled_function)
    while True:
        schedule.run_pending()
        time.sleep(15)


if __name__ == "__main__":
    run()
