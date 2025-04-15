

if __name__ == '__main__':
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

    # from utils.function import *
    # from backtests.backtests import *


    ############### 以下メモ用 ################
    # get_stock_data(ticker)で株価データフレームを返す
    # get_stock_minute_data(ticker)で分足の株価データフレームを返す
    ##########################################







######################################## function.py ########################################


import pandas as pd
import os
import talib as ta

def get_stock_data(ticker):
    file_path = os.path.join("data/daily", f"{ticker}.csv")
    # file_path = os.path.join("data/daily", f"{ticker}_daily.csv")

    # CSVを適切に読み込む
    df = pd.read_csv(file_path, index_col=0, parse_dates=True)

    # 列名の順番を指定して設定
    df.columns = ["Close", "High", "Low", "Open", "Volume"]

    # インデックスを datetime に変換（タイムゾーン削除）
    df.index = pd.to_datetime(df.index).tz_localize(None)  # ここを追加

    return df



def get_stock_data_test(ticker):
    file_path = os.path.join("data/daily", f"{ticker}.csv")

    # ヘッダーを2行使って読み込む
    df = pd.read_csv(file_path, header=[0, 1], index_col=0)

    # 不要な1行目（"Price"）を削除、2行目（"6146.T"）を列名にする
    df.columns = df.columns.droplevel(0)  # "Price" を削除

    # インデックス（日付）を datetime に変換
    # df.index = pd.to_datetime(df.index, format="%Y/%m/%d", errors='coerce')
    df.index = pd.to_datetime(df.index, errors='coerce')
    df = df.dropna()  # 日付変換に失敗した行は削除

    df.columns = ["Close", "High", "Low", "Open", "Volume"]
    df.index = df.index.tz_localize(None)  # タイムゾーンなし

    return df


def get_stock_minute_data(ticker):
    file_path = os.path.join("data/minute", f"{ticker}_minute.csv")
    
    # CSVを適切に読み込む
    df = pd.read_csv(file_path, index_col=0, parse_dates=True)

        # 列名の順番を指定して設定
    df.columns = ["Close", "High", "Low", "Open", "Volume"]
    
    # インデックスを datetime に変換（タイムゾーン削除）
    df.index = pd.to_datetime(df.index).tz_localize(None)  # ここを追加
    
    return df


def get_stock_data_old(ticker):
    file_path = os.path.join("data/daily", f"{ticker}.csv")
    
    # CSVを適切に読み込む
    df = pd.read_csv(file_path, skiprows=2, index_col=0, parse_dates=True)
    
    # 列名の順番を指定して設定
    df.columns = ["Close", "High", "Low", "Open", "Volume"]
    
    # インデックス（Date）を日付に変換
    df.index = pd.to_datetime(df.index)
    
    return df

from backtesting import Backtest

def run_optimized_backtest(df, strategy_class, maximize_metric='Return [%]', constraint=None, max_attempts=3):
    """
    売買ルールのクラス内のパラメータを使ってバックテストを最適化
    """
    bt = Backtest(df, strategy_class, trade_on_close=True)
    # クラスから最適化パラメータを取得
    optimize_params = strategy_class.get_optimize_params()

    attempt = 0
    optimized_result = None
    while attempt < max_attempts:
        try:
            optimized_result = bt.optimize(
                **optimize_params,
                maximize=maximize_metric,
                constraint=constraint
            )
            break  # 成功したらループを抜ける
        except Exception as e:
            print(f"最適化エラー (試行 {attempt+1}/{max_attempts}): {e}")
            attempt += 1
    
    if optimized_result is None:
        raise RuntimeError("最適化に失敗しました")
    
    best_params = {key: getattr(optimized_result._strategy, key) for key in optimize_params.keys()}
    final_result = bt.run(**best_params)
    
    return bt, final_result, best_params


######################################## backtests.py ########################################



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







######################################## main.py ########################################

if __name__ == '__main__':

    ############### 以下メモ用 ################
    # get_stock_data(ticker)で株価データフレームを返す
    # get_stock_minute_data(ticker)で分足の株価データフレームを返す
    ##########################################


    ticker = "5803.T_daily"
    ticker2 = "6146.T"
    df = get_stock_data(ticker)
    df.index.name = None  # ← インデックス名を削除
    df2 = get_stock_data_old(ticker2)

    print(df)
    print(df2)




    # バックテストの実行
    bt = Backtest(df2, SmaCross)
    result = bt.run()
    print(result)

    # 最適化の実行
    optimized_result = bt.optimize(
        short_window=range(5, 20, 5),
        long_window=range(10, 50, 10),
        maximize="Return [%]",
        constraint=lambda p: p.short_window < p.long_window  # 短期線 < 長期線
    )

    # print("最適化結果:")
    # print(optimized_result)

    # 最適化結果でバックテスト
    bt.plot()