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


############### 以下メモ用 ################
# get_stock_data(ticker)で株価データフレームを返す
# get_stock_minute_data(ticker)で分足の株価データフレームを返す
##########################################


if __name__ == '__main__':
    ticker = "7203.T"
    df = get_stock_data(ticker)
    
    print(df)

    bt = Backtest(df, RSICross, trade_on_close=True)
    # SmaCross,RSICross

    result = bt.optimize(
        ns=range(5, 25, 5),
        nl=range(5, 75, 5),
        maximize='Return [%]',
        constraint=lambda r: r.ns < r.nl
    )

    # result = bt.run()

    print("最適化結果:")
    print(result)

    # 最適なパラメータ（ns, nl）を出力
    best_ns = result._strategy.ns
    best_nl = result._strategy.nl
    print(f"最適なns: {best_ns}, 最適なnl: {best_nl}")

    bt.plot()
