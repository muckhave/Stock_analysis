from django import forms
from .models import StockSymbol

class BacktestForm(forms.Form):
    ticker = forms.MultipleChoiceField(
        label="銘柄コード（複数選択可）",
        choices=[],  # 動的に設定される
        widget=forms.CheckboxSelectMultiple,
    )
    strategy = forms.ChoiceField(
        label="戦略",
        choices=[
            ("SmaCross", "SMAクロス"),
            ("RSICross", "RSIクロス"),
            ("MACDCross", "MACDクロス"),
            ("BollingerBandStrategy", "ボリンジャーバンド"),
            ("RsiStrategy", "RSI戦略"),
            ("MaDeviationStrategy", "移動平均乖離戦略"),
            ("AtrTrailingStopStrategy", "ATRトレーリングストップ"),
            ("RSISignalStrategy", "RSIシグナル戦略"),
            ("RSIMACDStrategy", "RSI+MACD戦略"),
        ],
    )
    interval = forms.ChoiceField(
        label="インターバル",
        choices=[("daily", "日足"), ("minute", "分足")],
    )
    start_date = forms.DateField(label="開始日", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    end_date = forms.DateField(label="終了日", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    last_n_days = forms.IntegerField(label="直近N日", required=False)
    days_ago = forms.IntegerField(label="N日前から", required=False)
    lookback_days = forms.IntegerField(label="過去N日間", required=False)
    optimize = forms.BooleanField(label="最適化を実行", required=False, initial=True)

class StockSymbolForm(forms.ModelForm):
    class Meta:
        model = StockSymbol
        fields = ["code"]
        labels = {
            "code": "銘柄コード",
        }