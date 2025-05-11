from backtesting import Strategy
from backtesting.lib import Strategy
from backtesting.lib import crossover
from backtesting import Backtest
from backtesting.test import SMA
import pandas as pd
import numpy as np
# import pandas_ta as ta
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
        self.buy_signals = []  # 買いシグナルを記録するリスト
        self.sell_signals = []  # 売りシグナルを記録するリスト

    def next(self):
        if crossover(self.smaS, self.smaL):
            self.buy()
            self.buy_signals.append(self.data.index[-1])  # 買いシグナルの日時を記録
        elif crossover(self.smaL, self.smaS):
            self.position.close()
            self.sell_signals.append(self.data.index[-1])  # 売りシグナルの日時を記録


def RSI(close, n1, n2):
    rsiS = ta.RSI(close, timeperiod=n1)
    rsiL = ta.RSI(close, timeperiod=n2)
    return rsiS, rsiL

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
        if self.data.Close is None or len(self.data.Close) == 0:
            raise ValueError("データ 'Close' が空です。適切なデータを渡してください。")
        
        self.rsiS, self.rsiL = self.I(RSI, self.data.Close, self.ns, self.nl)
        self.buy_signals = []  # 買いシグナルを記録するリスト
        self.sell_signals = []  # 売りシグナルを記録するリスト

    def next(self):
        if crossover(self.rsiS, self.rsiL):
            self.buy()
            self.buy_signals.append(self.data.index[-1])  # 買いシグナルの日時を記録
        elif crossover(self.rsiL, self.rsiS):
            self.position.close()
            self.sell_signals.append(self.data.index[-1])  # 売りシグナルの日時を記録


def MACD(close, n1, n2, n3):
    macd, macdsignal, _ = ta.MACD(close, fastperiod=n1, slowperiod=n2, signalperiod=n3)
    return macd, macdsignal

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
        self.macd, self.macdsignal = self.I(MACD, self.data["Close"], self.n1, self.n2, self.n3)
        self.buy_signals = []  # 買いシグナルを記録するリスト
        self.sell_signals = []  # 売りシグナルを記録するリスト

    def next(self):
        if crossover(self.macd, self.macdsignal):
            self.buy()
            self.buy_signals.append(self.data.index[-1])  # 買いシグナルの日時を記録
        elif crossover(self.macdsignal, self.macd):
            self.position.close()
            self.sell_signals.append(self.data.index[-1])  # 売りシグナルの日時を記録
                     
# ボリンジャーバンド戦略
class BollingerBandStrategy(Strategy):
    # うまくいかない
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
        std = self.I(lambda close, window: pd.Series(close).rolling(window).std(), self.data["Close"], self.window)
        self.upper = mid + self.dev * std
        self.lower = mid - self.dev * std
        self.buy_signals = []  # 買いシグナルを記録するリスト
        self.sell_signals = []  # 売りシグナルを記録するリスト

    def next(self):
        if self.data.Close[-1] < self.lower[-1]:
            self.buy()
            self.buy_signals.append(self.data.index[-1])  # 買いシグナルの日時を記録
        elif self.data.Close[-1] > self.upper[-1]:
            self.position.close()
            self.sell_signals.append(self.data.index[-1])  # 売りシグナルの日時を記録


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
        self.rsi = self.I(lambda close: RSI(close, self.rsi_period, self.rsi_period)[0], self.data["Close"])
        self.buy_signals = []  # 買いシグナルを記録するリスト
        self.sell_signals = []  # 売りシグナルを記録するリスト

    def next(self):
        if self.rsi[-1] < self.rsi_buy:
            self.buy()
            self.buy_signals.append(self.data.index[-1])  # 買いシグナルの日時を記録
        elif self.rsi[-1] > self.rsi_sell:
            self.position.close()
            self.sell_signals.append(self.data.index[-1])  # 売りシグナルの日時を記録





# 移動平均乖離率戦略
class MaDeviationStrategy(Strategy):
    # うまくいった
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
        self.buy_signals = []  # 買いシグナルを記録するリスト
        self.sell_signals = []  # 売りシグナルを記録するリスト

    def next(self):
        deviation = (self.data.Close[-1] - self.ma[-1]) / self.ma[-1] * 100

        if deviation < -self.deviation_threshold:
            self.buy()
            self.buy_signals.append(self.data.index[-1])  # 買いシグナルの日時を記録
        elif deviation > self.deviation_threshold:
            self.position.close()
            self.sell_signals.append(self.data.index[-1])  # 売りシグナルの日時を記録




#  移動平均 + ATRトレーリングストップ

def ATR(data, period):
    """
    ATR (Average True Range) を計算する関数。

    Args:
        data (pd.DataFrame): 株価データフレーム（"High", "Low", "Close" 列を含む必要があります）
        period (int): ATR を計算する期間

    Returns:
        pd.Series: ATR の値
    """
    high = data["High"]
    low = data["Low"]
    close = data["Close"]
    return ta.ATR(high, low, close, timeperiod=period)

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
        self.atr = self.I(ATR, self.data, self.atr_period)  # 修正済み
        self.buy_signals = []  # 買いシグナルを記録するリスト
        self.sell_signals = []  # 売りシグナルを記録するリスト

    def next(self):
        if self.data.Close[-1] > self.ma[-1]:
            self.buy(sl=self.data.Close[-1] - self.atr_multiplier * self.atr[-1])
            self.buy_signals.append(self.data.index[-1])  # 買いシグナルの日時を記録
        elif self.data.Close[-1] < self.ma[-1]:
            self.position.close()
            self.sell_signals.append(self.data.index[-1])  # 売りシグナルの日時を記録



# RSIシグナル戦略
class RSISignalStrategy(Strategy):
    # うまくいかない
    rsi_period = 14  # RSIの計算期間
    rsi_signal = 50  # シグナル値

    @classmethod
    def get_optimize_params(cls):
        """
        最適化用のパラメータ範囲を定義
        """
        return {
            "rsi_period": range(10, 30, 2),  # RSI期間の範囲
            "rsi_signal": range(40, 60, 5),  # シグナル値の範囲
        }

    def init(self):
        """
        初期化処理: RSIを計算
        """
        self.rsi = self.I(ta.RSI, self.data["Close"], self.rsi_period)
        self.buy_signals = []  # 買いシグナルを記録するリスト
        self.sell_signals = []  # 売りシグナルを記録するリスト

    def next(self):
        """
        毎バーの処理: RSIがシグナル値を超えた場合に売買シグナルを生成
        """
        if self.rsi[-1] > self.rsi_signal:
            self.buy()  # RSIがシグナル値を超えたら買い
            self.buy_signals.append(self.data.index[-1])  # 買いシグナルの日時を記録
        elif self.rsi[-1] < self.rsi_signal:
            self.position.close()  # RSIがシグナル値を下回ったらポジションを閉じる
            self.sell_signals.append(self.data.index[-1])  # 売りシグナルの日時を記録


# RSI + MACD戦略
class RSIMACDStrategy(Strategy):
    rsi_period = 14
    rsi_buy_threshold = 40  # デフォルト30から緩和
    rsi_sell_threshold = 60  # デフォルト70から緩和
    macd_fast = 6  # デフォルト12から短縮
    macd_slow = 13  # デフォルト26から短縮
    macd_signal = 5  # デフォルト9から短縮

    @classmethod
    def get_optimize_params(cls):
        return {
            "rsi_period": range(10, 20, 2),
            "rsi_buy_threshold": range(20, 40, 5),
            "rsi_sell_threshold": range(60, 80, 5),
            "macd_fast": range(5, 15, 2),
            "macd_slow": range(15, 30, 2),
            "macd_signal": range(5, 15, 2),
        }

    def init(self):
        # 明示的に numpy.ndarray に変換
        close = np.asarray(self.data["Close"])
        
        # RSIの計算
        self.rsi = self.I(ta.RSI, close, self.rsi_period)
        
        # MACDの計算
        self.macd, self.macd_signal, _ = self.I(
            ta.MACD,
            close,  # numpy.ndarrayを渡す
            fastperiod=self.macd_fast,
            slowperiod=self.macd_slow,
            signalperiod=self.macd_signal,
        )
        self.buy_signals = []  # 買いシグナルを記録するリスト
        self.sell_signals = []  # 売りシグナルを記録するリスト

    def next(self):
        # 買い条件: RSIが売られすぎ & MACDがシグナルラインを上抜け
        if self.rsi[-1] < self.rsi_buy_threshold and crossover(self.macd, self.macd_signal):
            self.buy()
            self.buy_signals.append(self.data.index[-1])  # 買いシグナルの日時を記録

        # 売り条件: RSIが買われすぎ & MACDがシグナルラインを下抜け
        elif self.rsi[-1] > self.rsi_sell_threshold and crossover(self.macd_signal, self.macd):
            self.position.close()
            self.sell_signals.append(self.data.index[-1])  # 売りシグナルの日時を記録

