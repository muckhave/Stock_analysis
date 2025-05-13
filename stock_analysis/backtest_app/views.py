from django.shortcuts import render
from django.http import JsonResponse
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
from .utils import get_stock_data, get_stock_minute_data, filter_stock_data_by_period, fetch_and_save_all_symbols_all_intervals, run_optimized_backtest
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
from bokeh.embed import file_html
from bokeh.resources import CDN
matplotlib.use("Agg")  # GUIバックエンドを無効化

def rsi(data, period=14):
    """
    RSIを計算する関数。
    """
    close_prices = data['Close'].dropna().values  # 欠損値を削除して終値を取得
    close_prices = close_prices.astype(np.float64)  # 型を明示的にfloat64に変換
    print('rsi関数発動;j')
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
    buy_signal_tickers = []  # 直近2日で買いシグナルが出た銘柄
    best_ticker = None  # 最も利益が出た銘柄
    best_return = float('-inf')  # 最大利益の初期値
    best_graph_html = None  # 最も利益が出た銘柄のグラフHTMLを保存する変数

    print("リクエストメソッド:", request.method)

    if request.method == "POST":
        form = BacktestForm(request.POST)
        print("フォームのバリデーション:", form.is_valid())
        if form.is_valid():
            tickers = form.cleaned_data["ticker"]  # 選択された銘柄リストを取得
            print("選択された銘柄:", tickers)
            strategy_name = form.cleaned_data["strategy"]
            interval = form.cleaned_data["interval"]
            optimize = form.cleaned_data["optimize"]  # 最適化の選択を取得

            # 計測期間の取得
            start_date = form.cleaned_data.get("start_date")
            end_date = form.cleaned_data.get("end_date")
            last_n_days = form.cleaned_data.get("last_n_days")
            days_ago = form.cleaned_data.get("days_ago")
            lookback_days = form.cleaned_data.get("lookback_days")

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

            for ticker in tickers:
                ticker = ticker.strip()
                print(f"処理中の銘柄: {ticker}")

                # データ取得
                if interval == "daily":
                    df = get_stock_data(ticker, drop_na=True)
                elif interval == "minute":
                    df = get_stock_minute_data(ticker, drop_na=True)

                print(f"{ticker} のデータフレーム: {df.head()}")

                # 計測期間でデータをフィルタリング
                filtered_df = filter_stock_data_by_period(
                    df,
                    start_date=start_date,
                    end_date=end_date,
                    last_n_days=last_n_days,
                    days_ago=days_ago,
                    lookback_days=lookback_days,
                )

                try:
                    # バックテストの実行
                    bt, final_result, best_params, has_recent_buy_signal, has_recent_sell_signal, strategy_name = run_optimized_backtest(
                        filtered_df, strategy_class, optimize=optimize
                    )
                    print(f"{ticker} のバックテスト結果: {final_result}")

                    # 結果を保存
                    if has_recent_buy_signal:
                        buy_signal_tickers.append(ticker)

                    # 利益が最大の銘柄を更新
                    return_percentage = final_result["Return [%]"]
                    if return_percentage > best_return:
                        best_return = return_percentage
                        best_ticker = ticker

                        # 最も利益が出た銘柄のグラフHTMLを保存
                        grid_plot = bt.plot(open_browser=False)
                        best_graph_html = file_html(grid_plot, CDN, f"{ticker}_{strategy_name}_{interval}")

                except Exception as e:
                    print(f"{ticker} のバックテスト中にエラーが発生: {e}")
                    result_data = {"error": str(e)}
        else:
            print("フォームエラー:", form.errors)  # フォームエラーをログに出力
            result_data = {"error": "フォームの入力にエラーがあります。"}
    else:
        form = BacktestForm()

    print("最も利益が出た銘柄:", best_ticker)
    print("最も利益が出た銘柄のリターン:", best_return)

    return render(request, "backtest_app/index.html", {
        "form": form,
        "result_data": result_data,
        "graph_html": best_graph_html,  # 最も利益が出た銘柄のグラフを表示
        "buy_signal_tickers": buy_signal_tickers,
        "best_ticker": best_ticker,
        "best_return": best_return,
    })

def update_stock_data(request):
    """
    最新データを取得して保存するビュー。
    """
    if request.method == "POST":
        # 銘柄リストを指定（例: データベースや設定ファイルから取得）
        # symbols = ["7012.T", "7011.T", "6146.T"]  # 必要に応じて変更
        symbols = [
    "7012.T", "7011.T", "6146.T", "6857.T", "7203.T", "8306.T", "5803.T", "2432.T", "8316.T", "8035.T",
    "6758.T", "9983.T", "7013.T", "9984.T", "8411.T", "6501.T", "6098.T", "7974.T", "8136.T", "6861.T",
    "6920.T", "9104.T", "7267.T", "4676.T", "8058.T", "8725.T", "8766.T", "4063.T", "9101.T", "9432.T",
    "285A.T", "7182.T", "8001.T", "4502.T", "9749.T", "8031.T", "2914.T", "7741.T", "7936.T", "6702.T",
    "6981.T", "5016.T", "6503.T", "6752.T", "6902.T", "6273.T", "9433.T", "9434.T", "6723.T", "4568.T",
    "6954.T", "4755.T", "8630.T", "5401.T", "4751.T", "6367.T", "6532.T", "7751.T", "4661.T", "6701.T",
    "8604.T", "8002.T", "7261.T", "7201.T", "4519.T", "8053.T", "6762.T", "8801.T", "9021.T", "8309.T",
    "1605.T", "5108.T", "4543.T", "9020.T", "7735.T", "7003.T", "9107.T", "7270.T", "7269.T", "8802.T",
    "8308.T", "4004.T", "9501.T", "5411.T", "6301.T", "6201.T", "7832.T", "5801.T", "8591.T", "4503.T",
    "6526.T", "5406.T", "4901.T", "4578.T", "8750.T", "5838.T", "6594.T", "2502.T", "5802.T", "^N225"
    ]
        try:
            fetch_and_save_all_symbols_all_intervals(symbols)
            return JsonResponse({"status": "success", "message": "データを更新しました！"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "無効なリクエストです。"})
