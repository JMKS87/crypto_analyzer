from datetime import timedelta, datetime
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


def round_time(dt=None, date_delta=timedelta(minutes=1), to="average"):
    """
    Round a datetime object to a multiple of a timedelta
    dt : datetime.datetime object, default now.
    dateDelta : timedelta object, we round to a multiple of this, default 1 minute.
    from:  http://stackoverflow.com/questions/3463930/how-to-round-the-minute-of-a-datetime-object-python
    """
    round_to = date_delta.total_seconds()
    if dt is None:
        dt = datetime.now()
    seconds = (dt - dt.min).seconds

    if seconds % round_to == 0 and dt.microsecond == 0:
        rounding = (seconds + round_to / 2) // round_to * round_to
    else:
        if to == "up":
            rounding = (seconds + dt.microsecond / 1000000 + round_to) // round_to * round_to
        elif to == "down":
            rounding = seconds // round_to * round_to
        else:
            rounding = (seconds + round_to / 2) // round_to * round_to

    return dt + timedelta(0, rounding - seconds, -dt.microsecond)
