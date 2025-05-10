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
            bt = Backtest(df, strategy_class, cash=1000000, trade_on_close=True)
            result = bt.run()

            # HTMLグラフを生成
            grid_plot = bt.plot(open_browser=False)  # GridPlotオブジェクトを取得

            # HTMLファイルとして保存
            output_dir = os.path.join("data", "backtest_graph")
            os.makedirs(output_dir, exist_ok=True)  # ディレクトリが存在しない場合は作成
            output_file_path = os.path.join(output_dir, f"{ticker}_{strategy_name}_backtest.html")
            output_file(output_file_path)  # Bokehの出力先を設定
            save(grid_plot)  # GridPlotをHTMLファイルとして保存

            print(f"HTMLファイルを保存しました: {output_file_path}")  # 保存先をデバッグ出力

            # 保存されたHTMLファイルを読み取る
            with open(output_file_path, "r", encoding="utf-8") as f:
                graph_html = f.read()

            # テンプレートで参照しやすい形式に変換
            result_data = {
                "return_percentage": result["Return [%]"],
                "trade_count": result["# Trades"],
                "graph_html": graph_html,  # グラフHTMLをテンプレートに渡す
            }

            # 結果をテンプレートに渡す
            return render(request, "backtest_app/results.html", {"result": result_data})

    else:
        form = BacktestForm()

    return render(request, "backtest_app/index.html", {"form": form})
