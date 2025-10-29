from django.utils import timezone

DEFAULT_KLINES_TO_FETCH = 2_000
BINANCE_START_TIME = timezone.datetime(2017, 8, 1)

# approx. for daily; other intervals are much more advanced in time
COINALYZE_START_TIME = timezone.datetime(2024, 1, 1)
COINALYZE_EXCHANGE_CODES = {'P': 'Poloniex', 'V': 'Vertex', 'D': 'Bitforex', 'K': 'Kraken', 'U': 'Bithumb', 'B': 'Bitstamp', 'H': 'Hyperliquid', 'L': 'BitFlyer', 'M': 'BtcMarkets', 'I': 'Bit2c', 'E': 'MercadoBitcoin', 'N': 'Independent Reserve', 'G': 'Gemini', 'Y': 'Gate.io', '2': 'Deribit', '3': 'OKX', 'C': 'Coinbase', 'F': 'Bitfinex', 'J': 'Luno', '0': 'BitMEX', '7': 'Phemex', 'W': 'WOO X', '4': 'Huobi', '8': 'dYdX', '6': 'Bybit', 'A': 'Binance'}
COINALYZE_TRACKED_DATA = [
    # "OpenInterest",
    # "FundingRate",
    "PredictedFundingRate",
    # "LongShortRatio",
    # "LiquidationHistory",
]