from django.shortcuts import render
from .forms import BacktestForm
from .models import BacktestResult
from backtesting import Backtest
from .strategies import (
    SmaCross,
    RSICross,
    MACDCross,
    BollingerBandStrategy,
    RsiStrategy,
    MaDeviationStrategy,
    AtrTrailingStopStrategy,
    RSISignalStrategy,
    RSIMACDStrategy,
)
from .utils import get_stock_data, get_stock_minute_data, filter_stock_data_by_period
import talib
import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
import io
import base64
import matplotlib
import os  # ファイルパス操作のために必要
import mpld3  # mpld3をインポート
from bokeh.plotting import output_file, save  # Bokehの関数をインポート
matplotlib.use("Agg")  # GUIバックエンドを無効化

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

# データフレームの内容を出力
print("データフレームの内容:", df.head())

# RSIの計算結果を出力
rsi_values = rsi(df)
print(f"RSIの計算結果: {rsi_values}")

# MACDの計算結果を出力（型を明示的に変換）
close_prices = df['Close'].dropna().astype(np.float64).values
macd, macd_signal, macd_hist = talib.MACD(close_prices, fastperiod=12, slowperiod=26, signalperiod=9)
print(f"MACD: {macd}")
print(f"MACDシグナル: {macd_signal}")
print(f"MACDヒストグラム: {macd_hist}")

def index(request):
    result_data = None
    graph_html = None

    if request.method == "POST":
        form = BacktestForm(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data["ticker"]
            strategy_name = form.cleaned_data["strategy"]
            interval = form.cleaned_data["interval"]  # インターバルを取得

            # 計測期間の取得
            start_date = form.cleaned_data.get("start_date")
            end_date = form.cleaned_data.get("end_date")
            last_n_days = form.cleaned_data.get("last_n_days")
            days_ago = form.cleaned_data.get("days_ago")
            lookback_days = form.cleaned_data.get("lookback_days")

            # データ取得
            if interval == "daily":
                df = get_stock_data(ticker)
            elif interval == "minute":
                df = get_stock_minute_data(ticker)

            # 計測期間でデータをフィルタリング
            filtered_df = filter_stock_data_by_period(
                df,
                start_date=start_date,
                end_date=end_date,
                last_n_days=last_n_days,
                days_ago=days_ago,
                lookback_days=lookback_days,
            )

            # バックテストの実行
            strategy_class = {
                "SmaCross": SmaCross,
                "RSICross": RSICross,
                "MACDCross": MACDCross,
                "BollingerBandStrategy": BollingerBandStrategy,
                "RsiStrategy": RsiStrategy,
                "MaDeviationStrategy": MaDeviationStrategy,
                "AtrTrailingStopStrategy": AtrTrailingStopStrategy,
                "RSISignalStrategy": RSISignalStrategy,
                "RSIMACDStrategy": RSIMACDStrategy,
            }[strategy_name]

            bt = Backtest(filtered_df, strategy_class, cash=1000000, trade_on_close=True)
            result = bt.run()

            # グラフ生成
            grid_plot = bt.plot(open_browser=False)
            output_dir = os.path.join("data", "backtest_graph")
            os.makedirs(output_dir, exist_ok=True)
            output_file_path = os.path.join(output_dir, f"{ticker}_{strategy_name}_backtest.html")
            output_file(output_file_path)
            save(grid_plot)

            with open(output_file_path, "r", encoding="utf-8") as f:
                graph_html = f.read()

            result_data = {
                "return_percentage": result["Return [%]"],
                "trade_count": result["# Trades"],
            }

    else:
        form = BacktestForm()

    return render(request, "backtest_app/index.html", {
        "form": form,
        "result_data": result_data,
        "graph_html": graph_html,
    })
