from bulk_update_or_create import BulkUpdateOrCreateQuerySet
from django.db import models


class Exchange(models.Model):
    name = models.CharField(max_length=255, unique=True)


class Ticker(models.Model):
    SPOT = 'spot'
    FUTURES = 'futures'
    TICKER_TYPE_CHOICES = (
        (SPOT, 'spot'),
        (FUTURES, 'futures'),
    )

    class Meta:
        unique_together = (("name", "exchange", "type"),)

    name = models.CharField(max_length=255, unique=False)
    exchange = models.ForeignKey(to=Exchange, on_delete=models.CASCADE)
    type = models.CharField(
        max_length=20,
        choices=TICKER_TYPE_CHOICES,
        default=SPOT,
    )

    def __str__(self) -> str:
        rv = f"<{self.name}> on <({self.exchange})>"
        # if self.type != TickerType.SPOT:
        #     rv += f", type: {self.type}"
        return rv


class Chart(models.Model):
    class Meta:
        unique_together = (("ticker", "interval", "timestamp"),)

    objects = BulkUpdateOrCreateQuerySet.as_manager()

    timestamp = models.DateTimeField(null=False)
    end_timestamp = models.DateTimeField(null=True)
    ticker = models.ForeignKey(to=Ticker, on_delete=models.CASCADE)
    interval = models.DurationField(null=False)
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.FloatField()


class ChartAlarm(models.Model):
    ticker = models.ForeignKey(to=Ticker, on_delete=models.CASCADE)
    added = models.DateTimeField(auto_now_add=True)
    due = models.DateTimeField(default=None, null=True)
    fired = models.DateTimeField(default=None, null=True)
