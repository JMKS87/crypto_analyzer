import pandas as pd
import numpy as np
from backtesting import Strategy
from backtesting.lib import FractionalBacktest   # <-- allows fractional BTC

# ----------------------------------------------------------------------
# 1. Load the CSV
# ----------------------------------------------------------------------
FILE_PATH = r'C:\Users\jmks\Downloads\BTCUSDT_1h_20260825T233149Z.csv'

df = pd.read_csv(FILE_PATH, comment='#', parse_dates=['timestamp'])

df = df.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume',
})

df.set_index('timestamp', inplace=True)
df.index = pd.to_datetime(df.index, utc=True)
df.drop(columns=['end_timestamp'], inplace=True, errors='ignore')
df.sort_index(inplace=True)

# filter short timeframe
# df = df.loc['2026-07']
df = df.loc['2023-01-01':]
print(df.tail())


# ----------------------------------------------------------------------
# 2. RSI indicator that accepts a backtesting._Array
# ----------------------------------------------------------------------
def rsi(series, period: int = 14):
    """RSI (Wilder's smoothing). Accepts array-like, returns numpy array."""
    series = pd.Series(np.asarray(series, dtype=float))

    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()

    rs = avg_gain / avg_loss
    out = 100 - (100 / (1 + rs))
    return out.to_numpy()

# ----------------------------------------------------------------------
# 3. Strategy
# ----------------------------------------------------------------------
class RsiThreshold(Strategy):
    rsi_period = 14
    threshold = 52

    def init(self):
        self.rsi = self.I(rsi, self.data.Close, self.rsi_period)

    def next(self):
        if np.isnan(self.rsi[-1]) or np.isnan(self.rsi[-2]):
            return

        # Long when RSI crosses above 52
        if self.rsi[-1] > self.threshold and self.rsi[-2] <= self.threshold:
            if self.position.is_short:
                self.position.close()
            self.buy()

        # Short when RSI crosses below 52
        elif self.rsi[-1] < self.threshold and self.rsi[-2] >= self.threshold:
            if self.position.is_long:
                self.position.close()
            self.sell()

# ----------------------------------------------------------------------
# 4. Run with FractionalBacktest so we can trade fractional BTC
# ----------------------------------------------------------------------
bt = FractionalBacktest(
    df,
    RsiThreshold,
    cash=10_000,
    commission=0.000,
    exclusive_orders=True,
)

stats = bt.run()
trades = stats['_trades']
print(stats)

# bt.plot()
print('a')