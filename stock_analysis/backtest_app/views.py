from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .forms import BacktestForm, StockSymbolForm
from .models import BacktestResult, StockSymbol, SignalResult
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
    print('rsi関数発動;')
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
    best_result_data = None  # 初期化

    if request.method == "POST":
        # フォームの初期化と選択肢の設定
        stock_symbols = StockSymbol.objects.values_list("code", flat=True)
        form = BacktestForm(request.POST)
        form.fields["ticker"].choices = [
            (code, f"{code} ({get_stock_name(code)})") for code in stock_symbols
        ]

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

                    # フラグが出た場合、データベースに保存（上書き）
                    if has_recent_buy_signal or has_recent_sell_signal:
                        signal = "買い" if has_recent_buy_signal else "売り"
                        SignalResult.objects.update_or_create(
                            code=ticker,
                            defaults={
                                "name": ticker_name,
                                "date": filtered_df.index[-1].strftime("%Y-%m-%d"),
                                "best_params": {k: int(v) if isinstance(v, np.integer) else v for k, v in best_params.items()},
                                "strategy": strategy_name,
                                "signal": signal,
                            },
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
        form.fields["ticker"].choices = [
            (code, f"{code} ({get_stock_name(code)})") for code in stock_symbols
        ]

    # フラグが出た銘柄を取得してテンプレートに渡す
    buy_signals = SignalResult.objects.filter(signal="買い").order_by('-date')
    sell_signals = SignalResult.objects.filter(signal="売り").order_by('-date')

    return render(request, "backtest_app/index.html", {
        "form": form,
        "result_data": result_data,
        "graph_html": best_graph_html,
        "buy_signals": buy_signals,
        "sell_signals": sell_signals,
    })

def update_stock_data(request):
    """
    最新データを更新するビュー。
    """
    if request.method == "POST":
        # StockSymbol モデルから銘柄コードを取得
        symbols = list(StockSymbol.objects.values_list("code", flat=True))

        # データを取得して保存
        fetch_and_save_all_symbols_all_intervals(symbols)

        # 更新完了ページを表示
        return render(request, "backtest_app/update_complete.html")
    
    # GET リクエスト時のページを表示
    return render(request, "backtest_app/update_stock_data.html")

from django.db import IntegrityError

def settings_page(request):
    """
    設定ページのビュー。
    銘柄リストの管理を行う。
    """
    message = None  # メッセージを表示するための変数
    form = StockSymbolForm()  # フォームを初期化

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
