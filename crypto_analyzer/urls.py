"""crypto_analyzer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path

from charts import views


def hello(request):
    return HttpResponse("Hello world! Crypto-analyzer in progress!")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index),
    path("tv_api/config", views.tv_api_config),
    path("tv_api/time", views.tv_api_time),
    path("tv_api/symbols", views.tv_api_symbols),
    path("tv_api/history", views.tv_api_history),
    path("tv_api/search", views.tv_api_search),
    path("exchange_<str:exchange>/<str:ticker>", views.ticker_view),
    path("exchange_<str:exchange>", views.exchange_view),
    path("tv_chart/<str:ticker>", views.tv_chart, name='tv_chart'),
]
