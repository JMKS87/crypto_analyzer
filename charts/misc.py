from datetime import timedelta
from functools import wraps
from time import time
import logging

logger = logging.getLogger(__name__)


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        logger.info("func:%r args:[%r, %r] took: %2.4f sec" % (f.__name__, args, kw, te - ts))
        return result

    return wrap


def interval_to_timedelta(interval: str) -> timedelta:
    """Valid interval units: m, h, d, w, M, eg. 5m, 4h"""
    if interval.endswith("m"):
        return timedelta(minutes=int(interval[:-1]))
    elif interval.endswith("h"):
        return timedelta(hours=int(interval[:-1]))
    elif interval.endswith("d"):
        return timedelta(days=int(interval[:-1]))
    elif interval.endswith("D"):
        return timedelta(days=int(interval[:-1]))
    elif interval.endswith("w"):
        return timedelta(weeks=int(interval[:-1]))
    elif interval.endswith("M"):
        raise NotImplemented("Months requires some complex logic, not needed for now")
    raise ValueError("Unknown interval: <%s>", interval)
