# backtests/backtest_sma.py

from backtesting import Strategy
from backtesting import Backtest
from backtesting.lib import crossover
from backtesting.test import SMA
import talib as ta


class SmaCross(Strategy):
    # ns = 0.5
    # nl = 5
    ns = 5 
    nl = 25

    @classmethod
    def get_optimize_params(cls):
        return {
            "ns": range(5, 25, 5),
            "nl": range(5, 75, 5),
            # "ns": range(0.5, 2.5, 0.5),
            # "nl": range(0.5, 5, 0.5),
        }

    def init(self):
        self.smaS = self.I(SMA, self.data["Close"], self.ns)
        self.smaL = self.I(SMA, self.data["Close"], self.nl)

    def next(self):
        if crossover(self.smaS, self.smaL):
            self.buy()
        elif crossover(self.smaL, self.smaS):
            self.position.close()


def RSI(close,n1,n2):
    rsiS = ta.RSI(close,timeperiod=n1)
    rsiL = ta.RSI(close,timeperiod=n2)
    return rsiS,rsiL

class RSICross(Strategy):
    ns = 14
    nl = 28

    @classmethod
    def get_optimize_params(cls):
        return {
            "ns": range(5, 25, 5),
            "nl": range(5, 75, 5),
        }

    def init(self):
        self.rsiS,self.rsiL = self.I(RSI,self.data.Close,self.ns,self.nl)

    def next(self):
        if crossover(self.rsiS,self.rsiL):
            self.buy()
        elif crossover(self.rsiL,self.rsiS):
            self.position.close()


def MACD(close,n1,n2,n3):
    macd,macdsignal,_= ta.MACD(close,fastperiod=n1,slowperiod=n2,signalperiod=n3)

    return macd,macdsignal

class MACDCross(Strategy):
    n1 = 12 
    n2 = 26
    n3 = 9

    @classmethod
    def get_optimize_params(cls):
        return {
            "n1": range(5, 75, 5),
            "n2": range(10, 75, 5),
            "n3": range(10, 75, 5),
        }

    def init(self):
        self.macd,self.macdsignal= self.I(MACD,self.data["Close"],self.n1,self.n2,self.n3)

    def next(self):
        if crossover(self.macd,self.macdsignal):
            self.buy()
        elif crossover(self.macdsignal,self.macd):
            self.position.close() 
                     
# ボリンジャーバンド戦略
class BollingerBandStrategy(Strategy):
    window = 20
    dev = 2

    @classmethod
    def get_optimize_params(cls):
        return {
            "window": range(10, 50, 5),
            "dev": [1.5, 2, 2.5, 3],
        }

    def init(self):
        mid = self.I(SMA, self.data["Close"], self.window)
        std = self.I(lambda x, y: x.rolling(y).std(), self.data["Close"], self.window)
        self.upper = mid + self.dev * std
        self.lower = mid - self.dev * std

    def next(self):
        if self.data.Close[-1] < self.lower[-1]:
            self.buy()
        elif self.data.Close[-1] > self.upper[-1]:
            self.position.close()


# RSIオーバーソールド戦略
class RsiStrategy(Strategy):
    rsi_period = 14
    rsi_buy = 30
    rsi_sell = 70

    @classmethod
    def get_optimize_params(cls):
        return {
            "rsi_period": range(10, 30, 2),
            "rsi_buy": range(20, 40, 5),
            "rsi_sell": range(60, 80, 5),
        }

    def init(self):
        self.rsi = self.I(RSI, self.data["Close"], self.rsi_period)

    def next(self):
        if self.rsi[-1] < self.rsi_buy:
            self.buy()
        elif self.rsi[-1] > self.rsi_sell:
            self.position.close()





# 移動平均乖離率戦略
class MaDeviationStrategy(Strategy):
    ma_period = 20
    deviation_threshold = 5

    @classmethod
    def get_optimize_params(cls):
        return {
            "ma_period": range(10, 50, 5),
            "deviation_threshold": range(2, 10, 2),
        }

    def init(self):
        self.ma = self.I(SMA, self.data["Close"], self.ma_period)

    def next(self):
        deviation = (self.data.Close[-1] - self.ma[-1]) / self.ma[-1] * 100

        if deviation < -self.deviation_threshold:
            self.buy()
        elif deviation > self.deviation_threshold:
            self.position.close()




#  移動平均 + ATRトレーリングストップ
class AtrTrailingStopStrategy(Strategy):
    ma_period = 50
    atr_period = 14
    atr_multiplier = 2

    @classmethod
    def get_optimize_params(cls):
        return {
            "ma_period": range(20, 100, 10),
            "atr_period": range(10, 30, 5),
            "atr_multiplier": [1.5, 2, 2.5, 3],
        }

    def init(self):
        self.ma = self.I(SMA, self.data["Close"], self.ma_period)
        self.atr = self.I(ATR, self.data, self.atr_period)

    def next(self):
        if self.data.Close[-1] > self.ma[-1]:
            self.buy(sl=self.data.Close[-1] - self.atr_multiplier * self.atr[-1])
        elif self.data.Close[-1] < self.ma[-1]:
            self.position.close()

