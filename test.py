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
from utils.function import *
from backtesting import Strategy
from backtesting import Backtest
from backtesting.lib import crossover
from backtesting.test import SMA

############### 以下メモ用 ################
# get_stock_data(ticker)で株価データフレームを返す
# get_stock_minute_data(ticker)で分足の株価データフレームを返す
##########################################

class SmaCross(Strategy):
    ns = 5 
    nl = 25

    def init(self):
        self.smaS = self.I(SMA, self.data["Close"], self.ns)
        self.smaL = self.I(SMA, self.data["Close"], self.nl)

    def next(self):
        if crossover(self.smaS, self.smaL):
            self.buy()
        elif crossover(self.smaL, self.smaS):
            self.position.close()

if __name__ == '__main__':
    ticker = "7203.T"
    df = get_stock_data(ticker)
    
    print(df)

    bt = Backtest(df, SmaCross, trade_on_close=True)

    result = bt.optimize(
        ns=range(5, 25, 5),
        nl=range(5, 75, 5),
        maximize='Return [%]',
        constraint=lambda r: r.ns < r.nl
    )

    print("最適化結果:")
    print(result)

    # 最適なパラメータ（ns, nl）を出力
    best_ns = result._strategy.ns
    best_nl = result._strategy.nl
    print(f"最適なns: {best_ns}, 最適なnl: {best_nl}")

    bt.plot()
