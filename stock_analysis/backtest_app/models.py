from django.db import models

class BacktestResult(models.Model):
    ticker = models.CharField(max_length=10)
    strategy_name = models.CharField(max_length=50)
    return_percentage = models.FloatField()
    trade_count = models.IntegerField()
    best_params = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ticker} - {self.strategy_name}"
