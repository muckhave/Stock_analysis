from django import forms

class BacktestForm(forms.Form):
    ticker = forms.CharField(label="銘柄コード", max_length=10)
    strategy = forms.ChoiceField(
        label="戦略",
        choices=[
            ("SmaCross", "移動平均クロス戦略"),
            ("RSICross", "RSIクロス戦略"),
            ("MACDCross", "MACDクロス戦略"),
            ("BollingerBandStrategy", "ボリンジャーバンド戦略"),
            ("RsiStrategy", "RSIオーバーソールド戦略"),
            ("MaDeviationStrategy", "移動平均乖離率戦略"),
            ("AtrTrailingStopStrategy", "移動平均 + ATRトレーリングストップ戦略"),
            ("RSISignalStrategy", "RSIシグナル戦略"),
            ("RSIMACDStrategy", "RSI + MACD戦略"),
        ],
    )
    interval = forms.ChoiceField(
        label="データのインターバル",
        choices=[
            ("daily", "日足"),
            ("minute", "5分足"),
        ],
    )
    start_date = forms.DateField(label="開始日", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    end_date = forms.DateField(label="終了日", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    last_n_days = forms.IntegerField(label="直近の日数", required=False, min_value=1)
    days_ago = forms.IntegerField(label="指定日数前", required=False, min_value=1)
    lookback_days = forms.IntegerField(label="過去の日数", required=False, min_value=1)