import os
from dataclasses import fields
from datetime import timedelta, datetime

import django
import sys

# env variables to set
#DJANGO_SETTINGS_MODULE=crypto_analyzer.settings
#PYTHONPATH=S:\code\crypto_analyzer

# Add project root to Python path
sys.path.append('S:\code\crypto_analyzer')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crypto_analyzer.settings')
django.setup()

# Now you can use Django features
from charts.models import Ticker, Chart


def find_data_gaps(charts, interval=timedelta(minutes=1)):
    """
    Find gaps in time series data.

    Args:
        charts: QuerySet of Chart objects, ordered by timestamp
        interval: Expected interval between data points

    Returns:
        List of tuples (gap_start, gap_end) where gaps exist
    """
    if not charts.exists():
        return []

    gaps = []
    prev_end = None

    charts_objects = list(charts.values("timestamp"))
    for chart in charts_objects:
        if prev_end is not None and chart["timestamp"] - prev_end > interval:
            gaps.append((chart["timestamp"] - prev_end, prev_end, chart["timestamp"]))
        prev_end = chart["timestamp"]

    return gaps

def main():
    # Your script logic
    ticker = Ticker.objects.get(name="BTCUSDT")
    charts = Chart.objects.filter(ticker=ticker, interval="1m", timestamp__range=(datetime(2019, 11, 14, 12, 0), datetime(2025, 11, 14, 13, 0))).order_by("timestamp")
    gaps = find_data_gaps(charts)
    print(f'Found {charts.count()} objects')
    print(f'Found gaps: count: {len(gaps)}, {gaps}')
    print(f'a')

if __name__ == '__main__':
    main()
