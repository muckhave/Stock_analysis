from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .forms import BacktestForm, StockSymbolForm
from .models import BacktestResult, StockSymbol
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
from .utils import get_stock_data, get_stock_minute_data, filter_stock_data_by_period, fetch_and_save_all_symbols_all_intervals, run_optimized_backtest, get_stock_name
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
    """
    バックテストのメインページ。
    """
    result_data = None
    graph_html = None
    buy_signal_tickers = []
    sell_signal_tickers = []
    best_ticker = None
    best_ticker_name = None
    best_return = float('-inf')
    best_graph_html = None
    total_return = 0
    total_trades = 0
    ticker_count = 0

    if request.method == "POST":
        # フォームの初期化と選択肢の設定
        stock_symbols = StockSymbol.objects.values_list("code", flat=True)
        form = BacktestForm(request.POST)
        form.fields["ticker"].choices = [(code, code) for code in stock_symbols]

        if form.is_valid():
            tickers = form.cleaned_data["ticker"]
            strategy_name = form.cleaned_data["strategy"]
            interval = form.cleaned_data["interval"]
            optimize = form.cleaned_data["optimize"]

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
                try:
                    ticker = ticker.strip()
                    ticker_name = get_stock_name(ticker)
                    ticker_count += 1

                    # データ取得
                    if interval == "daily":
                        df = get_stock_data(ticker, drop_na=True)
                    elif interval == "minute":
                        df = get_stock_minute_data(ticker, drop_na=True)

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
                    bt, final_result, best_params, has_recent_buy_signal, has_recent_sell_signal, strategy_name = run_optimized_backtest(
                        filtered_df, strategy_class, optimize=optimize
                    )

                    # 結果を保存
                    if has_recent_buy_signal:
                        buy_signal_tickers.append(f"{ticker} ({ticker_name})")
                    if has_recent_sell_signal:
                        sell_signal_tickers.append(f"{ticker} ({ticker_name})")

                    # 利益が最大の銘柄を更新
                    return_percentage = final_result["Return [%]"]
                    total_return += return_percentage
                    total_trades += final_result["# Trades"]

                    if return_percentage > best_return:
                        best_return = return_percentage
                        best_ticker = ticker
                        best_ticker_name = ticker_name

                        # 最も利益が出た銘柄のグラフHTMLを保存
                        grid_plot = bt.plot(open_browser=False)
                        best_graph_html = file_html(grid_plot, CDN, f"{ticker}_{strategy_name}_{interval}")

                        # 最も利益が出た銘柄のバックテスト結果を保存
                        best_result_data = {
                            "return_percentage": final_result["Return [%]"],
                            "trade_count": final_result["# Trades"],
                            "best_params": best_params,
                            "recent_buy_signal": has_recent_buy_signal,
                            "recent_sell_signal": has_recent_sell_signal,
                        }

                except Exception as e:
                    print(f"{ticker} のバックテスト中にエラーが発生: {e}")

            # 平均リターンと平均取引回数を計算
            average_return = total_return / ticker_count if ticker_count > 0 else 0
            average_trades = total_trades / ticker_count if ticker_count > 0 else 0

            # バックテスト結果を result_data に保存
            result_data = {
                "best_ticker": f"{best_ticker} ({best_ticker_name})",
                "best_return": best_return,
                "best_result_data": best_result_data,
                "buy_signal_tickers": buy_signal_tickers,
                "sell_signal_tickers": sell_signal_tickers,
                "average_return": average_return,
                "average_trades": average_trades,
            }

        else:
            print("フォームエラー:", form.errors)
            result_data = {"error": "フォームの入力にエラーがあります。"}
    else:
        # GET リクエスト時にフォームを初期化
        stock_symbols = StockSymbol.objects.values_list("code", flat=True)
        form = BacktestForm()
        form.fields["ticker"].choices = [(code, code) for code in stock_symbols]

    return render(request, "backtest_app/index.html", {
        "form": form,
        "result_data": result_data,
        "graph_html": best_graph_html,
    })

def update_stock_data(request):
    """
    最新データを更新するビュー。
    """
    if request.method == "POST":
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

        fetch_and_save_all_symbols_all_intervals(symbols)

        return render(request, "backtest_app/update_complete.html")
    return render(request, "backtest_app/update_stock_data.html")

from django.db import IntegrityError

def settings_page(request):
    """
    設定ページのビュー。
    銘柄リストの管理を行う。
    """
    message = None  # メッセージを表示するための変数

    if request.method == "POST":
        if "delete" in request.POST:  # 削除ボタンが押された場合
            stock_id = request.POST.get("stock_id")
            stock = get_object_or_404(StockSymbol, id=stock_id)
            stock.delete()
            return redirect("settings_page")  # 設定ページにリダイレクト
        elif "add_bulk" in request.POST:  # 一括追加フォームが送信された場合
            bulk_codes = request.POST.get("bulk_codes", "")
            codes = [code.strip() for code in bulk_codes.split(",") if code.strip()]  # カンマ区切りで分割
            existing_codes = set(StockSymbol.objects.values_list("code", flat=True))  # 既存の銘柄コードを取得
            new_codes = [code for code in codes if code not in existing_codes]  # 重複を除外

            for code in new_codes:
                try:
                    StockSymbol.objects.create(code=code)
                except IntegrityError:
                    pass  # 重複エラーを無視

            message = f"{len(new_codes)} 件の銘柄コードを追加しました。"
        else:  # 通常のフォーム送信
            form = StockSymbolForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("settings_page")  # 設定ページにリダイレクト
    else:
        form = StockSymbolForm()

    # 現在の銘柄リストを取得
    symbols = StockSymbol.objects.all()

    # 銘柄コードから銘柄名を取得
    symbols_with_names = [
        {"id": symbol.id, "code": symbol.code, "name": get_stock_name(symbol.code)}
        for symbol in symbols
    ]

    return render(request, "backtest_app/settings_page.html", {
        "form": form,
        "symbols": symbols_with_names,
        "message": message,
    })
