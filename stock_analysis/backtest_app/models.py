from django.db import models

class StockSymbol(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="銘柄コード")

    def __str__(self):
        return self.code


class BacktestResult(models.Model):
    ticker = models.CharField(max_length=10)
    strategy_name = models.CharField(max_length=50)
    return_percentage = models.FloatField()
    trade_count = models.IntegerField()
    best_params = models.JSONField()  # JSONField を使用
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ticker} - {self.strategy_name}"
