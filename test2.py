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

def get_stock_data(ticker, drop_na=False, interpolate=False):
    """
    株価データを取得する関数。
    欠損値処理をオプションで追加可能。

    Args:
        ticker (str): 銘柄コード
        drop_na (bool): Trueの場合、欠損値を削除
        interpolate (bool): Trueの場合、欠損値を補完

    Returns:
        pd.DataFrame: 株価データフレーム
    """
    file_path = os.path.join("data/daily", f"{ticker}_daily.csv")

    # CSVを適切に読み込む
    df = pd.read_csv(file_path, index_col=0, parse_dates=True)

    # 列名の順番を指定して設定
    df.columns = ["Close", "High", "Low", "Open", "Volume"]

    # インデックスを datetime に変換（タイムゾーン削除）
    df.index = pd.to_datetime(df.index).tz_localize(None)

    # 欠損値処理
    if drop_na:
        # 欠損値を削除
        df = df.dropna()
    elif interpolate:
        # 欠損値を補完（線形補完を使用）
        df = df.interpolate()

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


def get_stock_minute_data(ticker, drop_na=False, interpolate=False):
    """
    分足データを取得する関数。
    欠損値処理をオプションで追加可能。

    Args:
        ticker (str): 銘柄コード
        drop_na (bool): Trueの場合、欠損値を削除
        interpolate (bool): Trueの場合、欠損値を補完

    Returns:
        pd.DataFrame: 分足データフレーム
    """
    file_path = os.path.join("data/minute", f"{ticker}_minute.csv")

    # CSVを適切に読み込む
    df = pd.read_csv(file_path, index_col=0, parse_dates=True)

    # 列名の順番を指定して設定
    df.columns = ["Close", "High", "Low", "Open", "Volume"]

    # インデックスを datetime に変換（タイムゾーン削除）
    df.index = pd.to_datetime(df.index).tz_localize(None)

    # 欠損値処理
    if drop_na:
        # 欠損値を削除
        df = df.dropna()
    elif interpolate:
        # 欠損値を補完（線形補完を使用）
        df = df.interpolate()

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


def get_stock_name(ticker, csv_path="data/stock_id.csv"):
    """
    銘柄コードを引数に与えると、その銘柄名を返す関数。

    Args:
        ticker (str): 銘柄コード（例: "7012.T"）
        csv_path (str): 東証プライム銘柄のCSVファイルパス

    Returns:
        str: 銘柄名（存在しない場合はNone）
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSVファイルが見つかりません: {csv_path}")
    
    # CSVファイルを読み込む
    df = pd.read_csv(csv_path)
    
    # 銘柄コードから ".T" を削除
    ticker_without_t = ticker.replace(".T", "")
    
    # 銘柄コードをキーにして銘柄名を取得
    stock = df[df["コード"] == ticker_without_t]
    if not stock.empty:
        return stock.iloc[0]["銘柄名"]
    else:
        return None

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



def filter_stock_data_by_period(df, start_date=None, end_date=None, last_n_days=None, days_ago=None, lookback_days=None):
    """
    指定した期間、直近の日数、または指定日数前から過去のデータを取得する関数。

    Args:
        df (pd.DataFrame): 株価データフレーム（インデックスはdatetime型）
        start_date (str or datetime, optional): 開始日（例: "2023-01-01"）
        end_date (str or datetime, optional): 終了日（例: "2023-12-31"）
        last_n_days (int, optional): 直近の日数（例: 30）
        days_ago (int, optional): 指定日数前（例: 10）
        lookback_days (int, optional): 過去のデータ日数（例: 5）

    Returns:
        pd.DataFrame: 指定された条件に基づく株価データ
    """
    # 指定日数前から過去のデータを取得
    if days_ago is not None and lookback_days is not None:
        end_date = df.index.max() - pd.Timedelta(days=days_ago)
        start_date = end_date - pd.Timedelta(days=lookback_days)
    # 直近の日数を取得
    elif last_n_days is not None:
        end_date = df.index.max()
        start_date = end_date - pd.Timedelta(days=last_n_days)
    
    # 開始日と終了日でフィルタリング
    if start_date:
        df = df[df.index >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df.index <= pd.to_datetime(end_date)]
    
    return df



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


# RSIシグナル戦略
class RSISignalStrategy(Strategy):
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

    def next(self):
        """
        毎バーの処理: RSIがシグナル値を超えた場合に売買シグナルを生成
        """
        if self.rsi[-1] > self.rsi_signal:
            self.buy()  # RSIがシグナル値を超えたら買い
        elif self.rsi[-1] < self.rsi_signal:
            self.position.close()  # RSIがシグナル値を下回ったらポジションを閉じる





######################################## main.py ########################################

if __name__ == '__main__':

    ############### 以下メモ用 ################
    # get_stock_data(ticker)で株価データフレームを返す
    # get_stock_minute_data(ticker)で分足の株価データフレームを返す
    ##########################################

    # 調べたい銘柄を定義
    tickers = ["7011.T", "6146.T", "7012.T"]


    ticker = "7011.T"
    ticker2 = "6146.T"
    ticker3 = "7012.T"
    df = get_stock_data(ticker)
    df.index.name = None  # ← インデックス名を削除
    df2 = get_stock_data_old(ticker2)
    df3 = get_stock_minute_data(ticker3,drop_na=True)

    recent_data = filter_stock_data_by_period(df, days_ago=0, lookback_days=9999)


    # bt, result, best_params  = run_optimized_backtest(recent_data,SmaCross)
    bt, result, best_params  = run_optimized_backtest(recent_data,RSICross)
    # bt, result, best_params  = run_optimized_backtest(recent_data,RSISignalStrategy)
    # bt, result, best_params  = run_optimized_backtest(df,MACDCross)
    # bt, result, best_params  = run_optimized_backtest(df,BollingerBandStrategy)
    # bt, result, best_params  = run_optimized_backtest(df,RsiStrategy)
    # bt, result, best_params  = run_optimized_backtest(df,MaDeviationStrategy)
    # bt, result, best_params  = run_optimized_backtest(df,AtrTrailingStopStrategy)
    print("最適化結果:")
    print(result)
    return_percentage = result['Return [%]']
    print(f"リターン: {return_percentage}%")
    print(f"ベストなパラメータ：{best_params}")

    # HTML出力先を指定
    output_dir = "backtest_results"  # 保存先フォルダ
    os.makedirs(output_dir, exist_ok=True)  # フォルダがなければ作成
    output_file = os.path.join(output_dir, "backtest_result.html")

    # プロットをHTMLファイルに保存
    bt.plot(filename=output_file)
    print(f"バックテスト結果を {output_file} に保存しました！")


