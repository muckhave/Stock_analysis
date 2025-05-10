from backtesting import Strategy
from backtesting.lib import Strategy
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
    short_window = 10
    long_window = 20

    def init(self):
        close = self.data.Close  # 終値を取得
        close = close[~np.isnan(close)]  # 欠損値を削除
        self.short_sma = self.I(sma, close, self.short_window)
        self.long_sma = self.I(sma, close, self.long_window)

    def next(self):
        if self.short_sma[-1] > self.long_sma[-1]:
            self.buy()
        elif self.short_sma[-1] < self.long_sma[-1]:
            self.sell()

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