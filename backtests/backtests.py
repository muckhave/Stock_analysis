# backtests/backtest_sma.py

from backtesting import Strategy
from backtesting import Backtest
from backtesting.lib import crossover
from backtesting.test import SMA
import talib as ta

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
                     