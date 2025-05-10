from backtesting import Strategy
from backtesting.lib import Strategy
from backtesting.lib import crossover
from backtesting import Backtest
from backtesting.test import SMA
import pandas as pd
import numpy as np
import pandas_ta as ta
import talib

def sma(data, period):
    """
    単純移動平均を計算する関数。
    """
    return talib.SMA(data, timeperiod=period)

class RSIMACDStrategy(Strategy):
    rsi_period = 14
    rsi_buy_threshold = 30
    rsi_sell_threshold = 70
    macd_fast = 12
    macd_slow = 26
    macd_signal = 9

    def init(self):
        close = self.data.Close  # 終値を取得
        close = close[~np.isnan(close)]  # 欠損値を削除
        self.rsi = self.I(talib.RSI, close, self.rsi_period)
        self.macd, self.macd_signal = self.I(
            lambda x: talib.MACD(x, fastperiod=self.macd_fast, slowperiod=self.macd_slow, signalperiod=self.macd_signal),
            close
        )

    def next(self):
        if self.rsi[-1] < self.rsi_buy_threshold and self.macd[-1] > self.macd_signal[-1]:
            self.buy()
        elif self.rsi[-1] > self.rsi_sell_threshold and self.macd[-1] < self.macd_signal[-1]:
            self.position.close()

class SmaCross(Strategy):
    ns = 5
    nl = 25

    @classmethod
    def get_optimize_params(cls):
        return {
            "ns": range(5, 25, 5),
            "nl": range(5, 75, 5),
        }

    def init(self):
        self.smaS = self.I(SMA, self.data["Close"], self.ns)
        self.smaL = self.I(SMA, self.data["Close"], self.nl)
        self.buy_signals = []  # 買いシグナルを記録するリスト
        self.sell_signals = []  # 売りシグナルを記録するリスト

    def next(self):
        if crossover(self.smaS, self.smaL):
            self.buy()
            self.buy_signals.append(self.data.index[-1])  # 買いシグナルの日時を記録
        elif crossover(self.smaL, self.smaS):
            self.position.close()
            self.sell_signals.append(self.data.index[-1])  # 売りシグナルの日時を記録

class BollingerBandStrategy(Strategy):
    window = 20
    dev = 2

    def init(self):
        close = self.data.Close  # 終値を取得
        close = close[~np.isnan(close)]  # 欠損値を削除
        self.mid = self.I(ta.sma, close, self.window)
        self.upper = self.mid + self.dev * self.I(ta.stdev, close, self.window)
        self.lower = self.mid - self.dev * self.I(ta.stdev, close, self.window)

    def next(self):
        if self.data.Close[-1] < self.lower[-1]:
            self.buy()
        elif self.data.Close[-1] > self.upper[-1]:
            self.position.close()