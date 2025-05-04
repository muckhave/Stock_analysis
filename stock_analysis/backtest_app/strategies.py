from backtesting import Strategy
import pandas as pd
import numpy as np
import pandas_ta as ta

class RSIMACDStrategy(Strategy):
    rsi_period = 14
    rsi_buy_threshold = 30
    rsi_sell_threshold = 70
    macd_fast = 12
    macd_slow = 26
    macd_signal = 9

    def init(self):
        close = self.data["Close"]
        self.rsi = self.I(ta.rsi, close, self.rsi_period)
        self.macd, self.macd_signal = self.I(
            lambda x: ta.macd(x, fast=self.macd_fast, slow=self.macd_slow, signal=self.macd_signal)[["MACD_12_26_9", "MACDs_12_26_9"]],
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
        close = self.data["Close"]
        self.short_sma = self.I(ta.sma, close, self.short_window)
        self.long_sma = self.I(ta.sma, close, self.long_window)

    def next(self):
        if self.short_sma[-1] > self.long_sma[-1]:
            self.buy()
        elif self.short_sma[-1] < self.long_sma[-1]:
            self.position.close()

class BollingerBandStrategy(Strategy):
    window = 20
    dev = 2

    def init(self):
        close = self.data["Close"]
        self.mid = self.I(ta.sma, close, self.window)
        self.upper = self.mid + self.dev * self.I(ta.stdev, close, self.window)
        self.lower = self.mid - self.dev * self.I(ta.stdev, close, self.window)

    def next(self):
        if self.data.Close[-1] < self.lower[-1]:
            self.buy()
        elif self.data.Close[-1] > self.upper[-1]:
            self.position.close()