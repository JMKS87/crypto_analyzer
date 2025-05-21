from bulk_update_or_create import BulkUpdateOrCreateQuerySet
from django.db import models


class Exchange(models.Model):
    name = models.CharField(max_length=255, unique=True)

TICKER_KIND_CHOICES = [
    ('Spot', 'Spot'),
    ('Futures', 'Futures'),
    ('OpenInterest', 'Open Interest'),
    ('FundingRate', 'Funding Rate'),
    ('PredictedFundingRate', 'Predicted Funding Rate'),
    ('LongShortRatio', 'Long Short Ratio'),
    ('LuquidationHistory', 'Liquidation History'),
]


class Ticker(models.Model):
    class Meta:
        unique_together = (("name", "exchange", "kind"),)
        constraints = [
            models.CheckConstraint(
                check=models.Q(kind__in=[choice[0] for choice in TICKER_KIND_CHOICES]),
                name='valid_ticker_type'
            )
        ]

    name = models.CharField(max_length=255, unique=False)
    exchange = models.ForeignKey(to=Exchange, on_delete=models.CASCADE)
    kind = models.CharField(max_length=255, choices=TICKER_KIND_CHOICES, default='spot')

    additional_info = models.JSONField(default=dict)

    def __str__(self) -> str:
        return (f"{'[' + str(self.kind) + '] ' if self.kind else ''}"
                f"<{self.name}> on <({self.exchange})>")


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


class LongShortChart(models.Model):
    class Meta:
        unique_together = (("ticker", "interval", "timestamp"),)

    objects = BulkUpdateOrCreateQuerySet.as_manager()

    timestamp = models.DateTimeField(null=False)
    ticker = models.ForeignKey(to=Ticker, on_delete=models.CASCADE)
    long = models.FloatField()
    short = models.FloatField()


class ChartAlarm(models.Model):
    ticker = models.ForeignKey(to=Ticker, on_delete=models.CASCADE)
    added = models.DateTimeField(auto_now_add=True)
    due = models.DateTimeField(default=None, null=True)
    fired = models.DateTimeField(default=None, null=True)


class ChartLastUpdated(models.Model):
    class Meta:
        unique_together = (("ticker", "interval"),)

    ticker = models.ForeignKey(to=Ticker, on_delete=models.CASCADE)
    interval = models.DurationField(null=False)
    last_updated = models.DateTimeField()
