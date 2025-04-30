import pandas as pd
import pandas_datareader.data as pdr
import matplotlib.pyplot as plt
import mplfinance as mpf
import datetime as dt
import talib as ta
import matplotlib.lines as mlines
import numpy as np
import requests
import yfinance as yf

from backtesting import Strategy
from backtesting import Backtest
from backtesting.lib import crossover
from backtesting.test import SMA

from utils.function import *
from backtests.backtests import *




if __name__ == '__main__':

    ############### 以下メモ用 ################
    # get_stock_data(ticker)で株価データフレームを返す
    # get_stock_minute_data(ticker)で分足の株価データフレームを返す
    ##########################################

    # 調べたい銘柄を定義
    tickers = ["7011.T", "6146.T", "7012.T"]


    ticker = "7011.T"
    ticker2 = "6146.T"
    ticker3 = "7012.T"
    df = get_stock_data(ticker)
    df.index.name = None  # ← インデックス名を削除
    df2 = get_stock_data_old(ticker2)
    df3 = get_stock_minute_data(ticker3,drop_na=True)

    recent_data = filter_stock_data_by_period(df, days_ago=0, lookback_days=9999)


    # bt, result, best_params  = run_optimized_backtest(recent_data,SmaCross)
    bt, result, best_params  = run_optimized_backtest(recent_data,RSICross)
    # bt, result, best_params  = run_optimized_backtest(recent_data,RSISignalStrategy)
    # bt, result, best_params  = run_optimized_backtest(df,MACDCross)
    # bt, result, best_params  = run_optimized_backtest(df,BollingerBandStrategy)
    # bt, result, best_params  = run_optimized_backtest(df,RsiStrategy)
    # bt, result, best_params  = run_optimized_backtest(df,MaDeviationStrategy)
    # bt, result, best_params  = run_optimized_backtest(df,AtrTrailingStopStrategy)
    print("最適化結果:")
    print(result)
    return_percentage = result['Return [%]']
    print(f"リターン: {return_percentage}%")
    print(f"ベストなパラメータ：{best_params}")

    # HTML出力先を指定
    output_dir = "backtest_results"  # 保存先フォルダ
    os.makedirs(output_dir, exist_ok=True)  # フォルダがなければ作成
    output_file = os.path.join(output_dir, "backtest_result.html")

    # プロットをHTMLファイルに保存
    # bt.plot(filename=output_file)
    print(f"バックテスト結果を {output_file} に保存しました！")

