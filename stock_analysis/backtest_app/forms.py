from django import forms

SYMBOL_CHOICES = [
    ("7012.T", "7012.T"), ("7011.T", "7011.T"), ("6146.T", "6146.T"), ("6857.T", "6857.T"), ("7203.T", "7203.T"),
    ("8306.T", "8306.T"), ("5803.T", "5803.T"), ("2432.T", "2432.T"), ("8316.T", "8316.T"), ("8035.T", "8035.T"),
    # 必要に応じてリストを続ける...
    ("^N225", "^N225"),
]

class BacktestForm(forms.Form):
    ticker = forms.MultipleChoiceField(
        label="銘柄コード（複数選択可）",
        choices=SYMBOL_CHOICES,
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