from django import forms

class BacktestForm(forms.Form):
    ticker = forms.CharField(label="銘柄コード", max_length=10)
    strategy = forms.ChoiceField(
        label="戦略",
        choices=[
            ("RSIMACDStrategy", "RSI + MACD 戦略"),
            ("SmaCross", "移動平均クロス"),
            ("BollingerBandStrategy", "ボリンジャーバンド戦略"),
        ],
    )