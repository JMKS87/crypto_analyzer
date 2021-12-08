from django.db import models


class Exchange(models.Model):
    name = models.CharField(max_length=255, unique=True)


class Ticker(models.Model):
    class Meta:
        unique_together = (("name", "exchange"),)

    name = models.CharField(max_length=255, unique=False)
    exchange = models.ForeignKey(to=Exchange, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"<{self.name}> on <({self.exchange})>"


class Chart(models.Model):
    class Meta:
        unique_together = (("ticker", "interval", "timestamp"),)

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
