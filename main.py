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


    ticker = "5803.T_daily"
    ticker2 = "6146.T"
    ticker3 = "285A.T"
    df = get_stock_data(ticker)
    df.index.name = None  # ← インデックス名を削除
    df2 = get_stock_data_old(ticker2)
    df3 = get_stock_minute_data(ticker3)

    # print(df)
    # print(df2)


    bt, result, best_params  = run_optimized_backtest(df,SmaCross)

    # # バックテストの実行
    # bt = Backtest(df2, SmaCross)
    # result = bt.run()
    # print(result)

    # # 最適化の実行
    # optimized_result = bt.optimize(
    #     ns=range(5, 20, 5),
    #     nl=range(10, 50, 10),
    #     maximize="Return [%]",
    #     constraint=lambda p: p.ns < p.nl  # ns < nl に変更
    # )

    # print("最適化結果:")
    # print(optimized_result)


    print(result)
    print(best_params)
    

    # 最適化結果でバックテスト
    bt.plot()


    