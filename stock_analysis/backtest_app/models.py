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


class SignalResult(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="銘柄コード")
    name = models.CharField(max_length=100, verbose_name="銘柄名")
    date = models.DateField(verbose_name="フラグ日付")
    best_params = models.JSONField(verbose_name="最適値")
    strategy = models.CharField(max_length=50, verbose_name="戦略名")
    signal = models.CharField(max_length=10, verbose_name="シグナル")  # "買い" または "売り"

    def __str__(self):
        return f"{self.code} - {self.signal}"


class OptimizationResult(models.Model):
    ticker = models.CharField(max_length=10)
    strategy_name = models.CharField(max_length=100)
    best_params = models.JSONField()
    final_result = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    interval = models.CharField(max_length=10, choices=[("daily", "日足"), ("minute", "5分足")], default="daily")  # 新しいフィールド

    def __str__(self):
        return f"{self.ticker} - {self.strategy_name}"
