from django import forms

class BacktestForm(forms.Form):
    ticker = forms.ChoiceField(
        label="銘柄コード",
        choices=[
            ("7011.T", "三菱重工業"),
            ("7203.T", "トヨタ自動車"),
            ("6758.T", "ソニーグループ"),
        ],
    )
    strategy = forms.ChoiceField(
        label="戦略",
        choices=[
            ("SmaCross", "移動平均クロス"),
            ("RSIMACDStrategy", "RSI + MACD 戦略"),
            ("BollingerBandStrategy", "ボリンジャーバンド戦略"),
        ],
    )