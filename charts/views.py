import time
from dataclasses import asdict
from datetime import datetime
from string import digits
from typing import Dict, Union, List

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
