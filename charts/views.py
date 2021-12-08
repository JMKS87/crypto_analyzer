from django.http import HttpResponse, HttpRequest
from django.shortcuts import render

# Create your views here.
from charts.models import Exchange, Ticker, Chart


def index(request: HttpRequest) -> HttpResponse:
    response = "Crypto Analyzer work in progress<br>Available exchanges: <br>"
    exchanges = Exchange.objects.all().order_by("name")
    for exchange in exchanges:
        response += f"<a href=/{exchange.name}>{exchange.name}</a><br>"
    return HttpResponse(response)


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
        response += f"{value.timestamp}: {value.open}<br>"
    response += "<br>Chart: <br> TODO"
    return HttpResponse(response)


def exchange_view(request: HttpRequest, exchange: str) -> HttpResponse:
    exchange = exchange.lower()
    response = f"Exchange: {exchange}, available tickers: <br>"
    exchange = Exchange.objects.get(name=exchange)
    tickers = Ticker.objects.filter(exchange=exchange).order_by("name")
    for ticker in tickers:
        response += f"<a href=/binance/{ticker.name}>{ticker.name}</a><br>"
    return HttpResponse(response)
