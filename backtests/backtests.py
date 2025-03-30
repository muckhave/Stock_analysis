# backtests/backtest_sma.py

from backtesting import Strategy
from backtesting import Backtest
from backtesting.lib import crossover
from backtesting.test import SMA
import talib as ta

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


def RSI(close,n1,n2):
    rsiS = ta.RSI(close,timeperiod=n1)
    rsiL = ta.RSI(close,timeperiod=n2)
    return rsiS,rsiL

class RSICross(Strategy):
    ns = 14
    nl = 28

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

