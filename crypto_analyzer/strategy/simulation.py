from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, List, Union, Any

from charts.models import Exchange, Ticker
from charts.tools import iterate_klines


def simulate_simple_strategy(
        ticker: str,
        win: float,
        loss: float,
        from_: Optional[datetime],
        to: Optional[datetime],
        capital: float = 1.0,
) -> Dict[str, Union[List[Dict], Dict]]:
    """
    Simulate one of the simplest strategies and return results.

    Rules:
    entry: "now", (ie. always want to enter trade, immediately after exiting previous one),
        at next kline OPEN
    exit: win or loss approached, exit at next kline OPEN
    Last entered trade (if active) is ignored.
    """
    from_ = from_ or datetime(year=2023, month=1, day=1)
    to = to or datetime(year=2023, month=1, day=5)

    results = {
        "params":
            {
                "ticker": ticker,
                "win": win,
                "loss": loss,
                "from_": from_,
                "to": to,
                "capital": capital,
             },
        "entries": [],
    }
    entry = None
    # set to multipliers of entry price
    win += 1
    loss = 1 - loss

    exchange = "binance"
    ticker = ticker.upper()
    exchange = Exchange.objects.get(name=exchange)
    ticker_object = Ticker.objects.get(exchange=exchange, name=ticker)
    klines = iterate_klines(ticker=ticker_object, from_=from_, to=to)


    exit = False
    for kline in klines:
        if not entry:
            entry = Entry(enter_time=kline.timestamp, enter_price=kline.open)
            continue
        if exit:
            exit = False
            entry.exit_time = kline.timestamp
            entry.exit_price = kline.open
            results["entries"].append(entry)
            entry = None
            continue
        if kline.high >= entry.enter_price*win:
            exit = True
            continue
        if kline.low <= entry.enter_price*loss:
            exit = True
            continue

    return results

@dataclass
class Entry:
    enter_time: datetime
    enter_price: float
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    long: bool = True
    size: float = 1.0

    @property
    def change_percent(self):
        if not self.exit_price:
            return None
        return ((self.exit_price - self.enter_price) / self.enter_price) * 100

    def to_json_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            **{"change_percent": self.change_percent},
        }
