import time
import io
import csv
from dataclasses import asdict
from datetime import datetime
from string import digits
from typing import Dict, Union, List

from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render

from django.urls import reverse

from charts.misc import interval_to_timedelta
from charts.models import Exchange, Ticker, Chart
from crypto_analyzer.strategy.simulation import simulate_simple_strategy

SUPPORTED_RESOLUTIONS = [
                "1",
                "3",
                "5",
                "15",
                "30",
                "60",
                "240",
                "D",
                "2D",
                "3D",
                "W"
                "M"
        ]


def index(request: HttpRequest) -> HttpResponse:
    response = "Crypto Analyzer work in progress<br>Available exchanges: <br>"
    exchanges = Exchange.objects.all().order_by("name")
    for exchange in exchanges:
        response += f"<a href=/exchange_{exchange.name}>{exchange.name}</a><br>"
    return HttpResponse(response)


def info(request: HttpRequest) -> HttpResponse:
    return render(request, "info.html")


def ticker_view(request: HttpRequest, exchange: str, ticker: str) -> HttpResponse:
    exchange = exchange.lower()
    ticker = ticker.upper()
    exchange = Exchange.objects.get(name=exchange)
    ticker_object = Ticker.objects.get(exchange=exchange, name=ticker)
    values = Chart.objects.filter(ticker=ticker_object).order_by("-timestamp")[:10]
    if not values:
        return HttpResponse("Sorry, no data")
    response = "Last values: <br>"
    for value in values:
        response += f"{value.timestamp}: {value.close}<br>"
    chart_url = reverse("tv_chart", kwargs={"ticker": ticker})
    response += f"<br>Chart: <br> <a href='{chart_url}'>click</a>"
    export_url = reverse("ticker_export_page", kwargs={"exchange": exchange.name, "ticker": ticker})
    response += f"<br>Export: <br> <a href='{export_url}'>export</a>"
    import_url = reverse("ticker_import", kwargs={"exchange": exchange.name, "ticker": ticker})
    response += f"<br>Import: <br> <a href='{import_url}'>import</a>"
    return HttpResponse(response)


def exchange_view(request: HttpRequest, exchange: str) -> HttpResponse:
    exchange = exchange.lower()
    response = f"Exchange: {exchange}, available tickers: <br>"
    exchange = Exchange.objects.get(name=exchange)
    tickers = Ticker.objects.filter(exchange=exchange).order_by("name")
    for ticker in tickers:
        response += f"<a href=/exchange_binance/{ticker.name}>{ticker.name}</a><br>"
    return HttpResponse(response)


def tv_api_config(request: HttpRequest) -> HttpResponse:
    config = {
        "supports_search": True,
        "supports_group_request": False,
        "supports_marks": False,  # TODO: worth tinkering with?
        "supports_timescale_marks": False,
        "supports_time": True,
        "exchanges": [
            {"value": "", "name": "All Exchanges", "desc": ""},
            {"value": "Binance", "name": "Binance", "desc": "Binance"},
        ],
        "symbols_types": [
            {"name": "All types", "value": ""},
            {"name": "Stock", "value": "stock"},
            {"name": "Index", "value": "index"},
        ],
        "supported_resolutions": SUPPORTED_RESOLUTIONS,
    }
    return JsonResponse(config)


def tv_api_time(request: HttpRequest) -> HttpResponse:
    return HttpResponse(str(int(time.time())))


def tv_api_symbols(request: HttpRequest) -> HttpResponse:
    ticker = request.GET.get("symbol")
    data = {
        "name": ticker,
        "exchange-traded": "Binance",
        "exchange-listed": "Binance",
        "timezone": "Europe/Warsaw",
        "minmov": 1,
        "minmov2": 0,
        "pointvalue": 1,
        "session": "24x7",
        "has_intraday": True,
        "has_no_volume": False,
        "description": ticker,
        "type": "crypto",
        "supported_resolutions": SUPPORTED_RESOLUTIONS,
        "pricescale": 100,
        "ticker": ticker,
        # available intervals @ backend, regardless of intervals available @ frontend
        # (interpolated from available intervals)
        "intraday-multipliers": [
            "1",
        ],
    }

    return JsonResponse(data)


def tv_api_history(request: HttpRequest) -> HttpResponse:
    ticker = request.GET.get("symbol")
    countback = int(request.GET.get("countback"))
    resolution = request.GET.get("resolution")
    if resolution and resolution[-1].isdigit():
        resolution += "m"
    resolution = interval_to_timedelta(resolution)
    from_ = int(request.GET.get("from"))
    to = int(request.GET.get("to"))
    from_dt = datetime.fromtimestamp(from_)
    to_dt = datetime.fromtimestamp(to)
    exchange = "binance"
    ticker = ticker.upper()
    exchange = Exchange.objects.get(name=exchange)
    ticker_object = Ticker.objects.get(exchange=exchange, name=ticker)
    klines = (
        Chart.objects.filter(ticker=ticker_object, interval=resolution)
        .filter(timestamp__range=(from_dt, to_dt))
        .order_by("timestamp")
    )
    # no data for selected time range => get last data
    if not klines:
        klines = (
            Chart.objects.filter(ticker=ticker_object, interval=resolution)
            .order_by("timestamp")[countback:]
        )
    data = {
        "s": "ok",
        "t": [],
        "o": [],
        "h": [],
        "l": [],
        "c": [],
        "v": [],
    }
    for kline in klines:
        data["t"].append(kline.timestamp.timestamp())
        data["o"].append(kline.open)
        data["h"].append(kline.high)
        data["l"].append(kline.low)
        data["c"].append(kline.close)
        data["v"].append(kline.volume)
    return JsonResponse(data)


def tv_api_search(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("query")
    type_ = request.GET.get("type")
    exchange = request.GET.get("exchange").lower() or "binance"
    limit = int(request.GET.get("limit"))

    tickers = []
    exchange = Exchange.objects.get(name=exchange)
    ticker_objects = Ticker.objects.filter(Q(exchange=exchange), Q(name__icontains=query))[:limit]
    for ticker in ticker_objects:
        single = {
            "symbol": ticker.name,
            "full_name": ticker.name,
            "description": ticker.name,
            "exchange": exchange.name,
            "type": "crypto",
        }
        tickers.append(single)
    return JsonResponse(tickers, safe=False)


def tv_chart(request: HttpRequest, ticker: str) -> HttpResponse:
    return render(request, "chart.html", context={"ticker": ticker})


def get_template_data(results: Dict[str, Union[List[Dict], Dict]]) -> Dict:
    entries_no = len(results["entries"])
    params = results["params"]
    capital = params["capital"]
    tr = 0
    stats = {
            "entries": entries_no,
            "winners": 0,
            "losers": 0,
            "percent_win": None,
            "total_return": None,
            "total_return_percent": None,
        }
    data = {
        "raw_data": results,
        "params": params,
        "stats": stats,
            }

    for entry in results["entries"]:
        winner = (entry.enter_price < entry.exit_price) and entry.long
        stats["winners"] += winner
        tr += entry.change_percent/100 * entry.size

    stats["total_return"] = tr
    stats["total_return_percent"] = None if not tr \
        else ((tr * capital) / capital) * 100
    stats["losers"] = data["stats"]["entries"] - data["stats"]["winners"]
    stats["percent_win"] = None if not entries_no \
        else ((stats["winners"] / entries_no) * 100)
    return data

def simulate(request: HttpRequest, ticker: str) -> HttpResponse:
    as_json = request.GET.get("json", False)
    win = float(request.GET.get("win", 0.01))
    loss = float(request.GET.get("loss", 0.005))
    try:
        from_ = datetime.strptime(request.GET.get("from"), "%Y-%m-%d")
    except TypeError:
        from_ = None
    try:
        to = datetime.strptime(request.GET.get("to"), "%Y-%m-%d")
    except TypeError:
        to = None
    results = simulate_simple_strategy(ticker, win=win, loss=loss, from_=from_, to=to)

    if as_json:
        json_results = dict(results)
        json_results["entries"] = [
                entry.to_json_string()
                for entry in json_results["entries"]
        ]
        return JsonResponse(json_results)

    template_data = get_template_data(results)
    return render(request, "simulation_results.html", context={"data": template_data})


def ticker_export_page(request: HttpRequest, exchange: str, ticker: str) -> HttpResponse:
    return render(request, "export_ticker.htm", context={"exchange": exchange, "ticker": ticker})


def ticker_export_download(request: HttpRequest, exchange: str, ticker: str) -> HttpResponse:
    """Produce CSV for selected ticker.
    Query params supported:
      - interval (optional, parsed via interval_to_timedelta)
      - start_date (optional, 'YYYY-MM-DD')
      - end_date (optional, 'YYYY-MM-DD')
      - columns (optional, comma-separated column names). Defaults to timestamp,open,high,low,close,volume
    """
    exch_name = exchange.lower()
    ticker_name = ticker.upper()

    interval_param = request.GET.get("interval")
    interval = None
    if interval_param:
        try:
            interval = interval_to_timedelta(interval_param)
        except Exception:
            interval = None

    def _parse_date(val):
        if not val:
            return None
        try:
            return datetime.strptime(val, "%Y-%m-%d")
        except Exception:
            return None

    from_dt = _parse_date(request.GET.get("start_date"))
    to_dt = _parse_date(request.GET.get("end_date"))

    try:
        exchange_obj = Exchange.objects.get(name=exch_name)
    except Exchange.DoesNotExist:
        return HttpResponse("Exchange not found", status=404)
    try:
        ticker_obj = Ticker.objects.get(exchange=exchange_obj, name=ticker_name)
    except Ticker.DoesNotExist:
        return HttpResponse("Ticker not found", status=404)

    qs = Chart.objects.filter(ticker=ticker_obj)
    if interval:
        qs = qs.filter(interval=interval)
    if from_dt and to_dt:
        qs = qs.filter(timestamp__range=(from_dt, to_dt))
    elif from_dt:
        qs = qs.filter(timestamp__gte=from_dt)
    elif to_dt:
        qs = qs.filter(timestamp__lte=to_dt)
    qs = qs.order_by("timestamp")

    columns_param = request.GET.get("columns")
    if columns_param:
        columns = [c.strip() for c in columns_param.split(",") if c.strip()]
    else:
        # default columns (omit ticker and interval since they are in meta)
        columns = ["timestamp", "end_timestamp", "open", "high", "low", "close", "volume"]

    output = io.StringIO()
    # write metadata comments at top of file
    output.write(f"# meta_exchange: {exchange_obj.name}\n")
    output.write(f"# meta_ticker: {ticker_name}\n")
    output.write(f"# meta_interval: {interval_param or 'all'}\n")
    output.write(f"# generated_at: {datetime.utcnow().isoformat()}Z\n")

    writer = csv.writer(output)
    writer.writerow(columns)

    for row_obj in qs:
        row = []
        for col in columns:
            if col == "timestamp":
                row.append(row_obj.timestamp.isoformat())
            elif col == "end_timestamp":
                row.append(row_obj.end_timestamp.isoformat() if row_obj.end_timestamp else "")
            elif col == "ticker":
                # output ticker name rather than the FK object
                row.append(row_obj.ticker.name if row_obj.ticker else "")
            elif col == "interval":
                # display interval in a readable form (seconds) or as string
                row.append(str(row_obj.interval))
            elif hasattr(row_obj, col):
                val = getattr(row_obj, col)
                row.append(val)
            else:
                row.append("")
        writer.writerow(row)

    csv_data = output.getvalue()
    output.close()

    # include server timestamp to make filename unique
    server_ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"{ticker_name}_{interval_param or 'all'}_{server_ts}.csv"
    response = HttpResponse(csv_data, content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def ticker_import(request: HttpRequest, exchange: str, ticker: str) -> HttpResponse:
    """Upload CSV produced by ticker_export_download and import rows into Chart.

    GET: simple HTML upload form
    POST: accepts file field 'file' (multipart/form-data). Returns a plain text summary.
    """
    if request.method == "GET":
        # minimal upload form
        html = (
            f"<html><body>"
            f"<h1>Import for {exchange}/{ticker}</h1>"
            f"<form method='POST' enctype='multipart/form-data'>"
            f"<input type='file' name='file' accept='.csv' required>"
            f"<button type='submit'>Upload</button>"
            f"</form></body></html>"
        )
        return HttpResponse(html)

    # POST - process upload
    upload = request.FILES.get("file")
    if not upload:
        return HttpResponse("No file uploaded", status=400)

    try:
        raw = upload.read().decode("utf-8")
    except Exception:
        return HttpResponse("Failed to read uploaded file (expecting utf-8)", status=400)

    lines = raw.splitlines()
    meta = {}
    data_lines = []
    for line in lines:
        if line.startswith("#"):
            # expected format: '# meta_key: value'
            if ":" in line:
                keyval = line[1:].strip().split(":", 1)
                if len(keyval) == 2:
                    key = keyval[0].strip()
                    val = keyval[1].strip()
                    meta[key] = val
        else:
            # first non-comment lines and the rest are CSV
            data_lines.append(line)
    if not data_lines:
        return HttpResponse("No CSV data found in uploaded file", status=400)

    csv_text = "\n".join(data_lines)
    reader = csv.DictReader(io.StringIO(csv_text))

    meta_exchange = meta.get("meta_exchange", exchange).lower()
    meta_ticker = meta.get("meta_ticker", ticker).upper()
    meta_interval = meta.get("meta_interval")

    # validate exchange/ticker from meta vs URL
    if meta_exchange and meta_exchange.lower() != exchange.lower():
        return HttpResponse("Exchange in file metadata does not match URL", status=400)
    if meta_ticker and meta_ticker.upper() != ticker.upper():
        return HttpResponse("Ticker in file metadata does not match URL", status=400)

    try:
        exchange_obj = Exchange.objects.get(name=exchange.lower())
    except Exchange.DoesNotExist:
        return HttpResponse("Exchange not found", status=404)
    try:
        ticker_obj = Ticker.objects.get(exchange=exchange_obj, name=ticker.upper())
    except Ticker.DoesNotExist:
        return HttpResponse("Ticker not found", status=404)

    interval_td = None
    if meta_interval:
        try:
            interval_td = interval_to_timedelta(meta_interval)
        except Exception:
            interval_td = None

    created = 0
    updated = 0
    errors = []

    with transaction.atomic():
        for i, row in enumerate(reader, start=1):
            try:
                ts_raw = row.get("timestamp")
                ts = None
                if ts_raw:
                    # fromisoformat supports offsets like +00:00
                    ts = datetime.fromisoformat(ts_raw)
                end_raw = row.get("end_timestamp") or ""
                end_ts = datetime.fromisoformat(end_raw) if end_raw else None
                open_v = float(row.get("open")) if row.get("open") not in (None, "") else 0.0
                high_v = float(row.get("high")) if row.get("high") not in (None, "") else 0.0
                low_v = float(row.get("low")) if row.get("low") not in (None, "") else 0.0
                close_v = float(row.get("close")) if row.get("close") not in (None, "") else 0.0
                vol_v = float(row.get("volume")) if row.get("volume") not in (None, "") else 0.0

                # prefer interval from meta, else try to parse from row if present
                row_interval = interval_td
                if not row_interval and "interval" in row and row.get("interval"):
                    try:
                        row_interval = interval_to_timedelta(row.get("interval"))
                    except Exception:
                        row_interval = None

                # update_or_create based on unique_together (ticker, interval, timestamp)
                lookup = {"ticker": ticker_obj, "timestamp": ts}
                if row_interval:
                    lookup["interval"] = row_interval
                else:
                    # if no interval available, set to zero timedelta
                    lookup["interval"] = interval_to_timedelta("1m") if False else None

                defaults = {
                    "end_timestamp": end_ts,
                    "open": open_v,
                    "high": high_v,
                    "low": low_v,
                    "close": close_v,
                    "volume": vol_v,
                }

                # If lookup['interval'] is None, remove it from lookup and try to match only by timestamp and ticker
                if lookup.get("interval") is None:
                    lookup.pop("interval", None)
                    obj, created_flag = Chart.objects.update_or_create(
                        ticker=lookup["ticker"], timestamp=lookup["timestamp"], defaults=defaults
                    )
                else:
                    obj, created_flag = Chart.objects.update_or_create(
                        ticker=lookup["ticker"], interval=lookup["interval"], timestamp=lookup["timestamp"], defaults=defaults
                    )

                if created_flag:
                    created += 1
                else:
                    updated += 1
            except Exception as e:
                errors.append(f"line {i}: {e}")

    summary = f"Imported rows: created={created}, updated={updated}, errors={len(errors)}"
    if errors:
        summary += "\n" + "\n".join(errors)
    return HttpResponse(summary, content_type="text/plain")

