from binance import Client
# import pandas as pd
import time

# Initialize client for USD-M Futures (NO base_url needed if upgraded)
client = Client(api_key='YOUR_API_KEY', api_secret='YOUR_API_SECRET')


def get_futures_klines():
    try:
        # Calculate timestamps for the last 24 hours
        end_time = int(time.time() * 1000)  # Current time in milliseconds
        start_time = end_time - (24 * 60 * 60 * 1000)  # 24 hours ago

        # Fetch futures klines
        f_klines = client.futures_klines(
            symbol='BTCUSDT',
            interval=Client.KLINE_INTERVAL_1HOUR,
            startTime=start_time,
            endTime=end_time,
            limit=24
        )
        klines = client.get_klines(
            symbol='BTCUSDT',
            interval=Client.KLINE_INTERVAL_1HOUR,
            startTime=start_time,
            endTime=end_time,
            limit=24
        )
        exit(0)

        # Convert to DataFrame
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ], dtype=float)

        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]

    except Exception as e:
        print(f"Error: {e}")
        return None


# Execute
if __name__ == '__main__':
    data = get_futures_klines()
    if data is not None:
        print(data)