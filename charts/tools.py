from datetime import datetime
from typing import Optional, Iterator

from charts.models import Ticker, Chart


def iterate_klines(
        ticker: Ticker, from_: Optional[datetime], to=Optional[datetime], interval: str = "1m"
) -> Iterator[Chart]:
    klines = (
        Chart.objects.filter(ticker=ticker, interval=interval)
        .filter(timestamp__range=(from_, to))
        .order_by("timestamp")
    )
    for kline in klines:
        yield kline
