from django.shortcuts import render
from .forms import BacktestForm
from .models import BacktestResult
from backtesting import Backtest
from .strategies import RSIMACDStrategy, SmaCross, BollingerBandStrategy
from .utils import get_stock_data
import talib
import numpy as np
import pandas as pd
import json

def rsi(data, period=14):
    """
    RSIを計算する関数。
    """
    close_prices = data['Close'].dropna().values  # 欠損値を削除して終値を取得
    close_prices = close_prices.astype(np.float64)  # 型を明示的にfloat64に変換
    return talib.RSI(close_prices, timeperiod=period)

def filter_serializable(data):
    """
    JSON にシリアライズ可能なデータのみを抽出する関数。
    """
    return {k: v for k, v in data.items() if is_json_serializable(v)}

def is_json_serializable(value):
    try:
        json.dumps(value)
        return True
    except (TypeError, OverflowError):
        return False

df = pd.DataFrame({
    'Open': [100, 102, 104],
    'High': [105, 107, 109],
    'Low': [95, 97, 99],
    'Close': [102, 104, 106],
    'Volume': [1000, 1100, 1200]
})

print("データフレームの内容:", df.head())
print("RSIの計算結果:", rsi(df))

def index(request):
    if request.method == "POST":
        form = BacktestForm(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data["ticker"]
            strategy_name = form.cleaned_data["strategy"]

            # 戦略クラスを選択
            strategy_class = {
                "RSIMACDStrategy": RSIMACDStrategy,
                "SmaCross": SmaCross,
                "BollingerBandStrategy": BollingerBandStrategy,
            }[strategy_name]

            # データ取得とバックテスト実行
            df = get_stock_data(ticker)
            bt = Backtest(df, strategy_class, cash=100000, trade_on_close=True)
            result = bt.run()

            # テンプレートで参照しやすい形式に変換
            result_data = {
                "return_percentage": result["Return [%]"],
                "trade_count": result["# Trades"],
                "equity_curve": result["_equity_curve"].to_dict(),  # 必要に応じて加工
            }

            # 結果をテンプレートに渡す
            return render(request, "backtest_app/results.html", {"result": result_data})

    else:
        form = BacktestForm()

    return render(request, "backtest_app/index.html", {"form": form})
