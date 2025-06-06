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
from datetime import datetime

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

    # インデックスを datetime に変換
    df.index = pd.to_datetime(df.index)
    df.index = df.index.tz_localize(None)  # タイムゾーンなし
    df.index = df.index.floor('D')


    # 欠損値処理
    if drop_na:
        # 欠損値を削除
        df = df.dropna()
    elif interpolate:
        # 欠損値を補完（線形補完を使用）
        df = df.interpolate()
    
    print(df)
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

    # インデックスを datetime に変換
    df.index = pd.to_datetime(df.index)
    df.index = df.index.tz_localize(None)  # タイムゾーンなし

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
    bt = Backtest(df, strategy_class, trade_on_close=True, cash=100000)
    optimize_params = strategy_class.get_optimize_params()

    attempt = 0
    optimized_result = None
    while attempt < max_attempts:
        try:
            print(f"最適化試行 {attempt+1}/{max_attempts} を開始します...")
            print("最適化パラメータ:", optimize_params)
            optimized_result = bt.optimize(
                **optimize_params,
                maximize=maximize_metric,
                constraint=constraint
            )
            break
        except Exception as e:
            print(f"最適化エラー (試行 {attempt+1}/{max_attempts}): {e}")
            print("データの先頭:", df.head())
            print("データの末尾:", df.tail())
            print("データの行数:", len(df))
            attempt += 1

    if optimized_result is None:
        raise RuntimeError("最適化に失敗しました")

    best_params = {key: getattr(optimized_result._strategy, key) for key in optimize_params.keys()}
    final_result = bt.run(**best_params)

    # 戦略インスタンスを取得
    strategy_instance = final_result._strategy

    # 戦略名を取得
    strategy_name = type(strategy_instance).__name__

    # 直近2日に買いシグナルがあるかを判定
    if len(df) >= 2:
        recent_buy_signals = [
            signal for signal in strategy_instance.buy_signals
            if signal >= df.index[-2]
        ]
        recent_sell_signals = [
            signal for signal in strategy_instance.sell_signals
            if signal >= df.index[-2]
        ]
    else:
        recent_buy_signals = []
        recent_sell_signals = []

    has_recent_buy_signal = len(recent_buy_signals) > 0
    has_recent_sell_signal = len(recent_sell_signals) > 0

    print("最適化が成功しました。")
    return bt, final_result, best_params, has_recent_buy_signal, has_recent_sell_signal, strategy_name


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






def save_backtest_results(result, best_params, ticker_id, ticker_name, interval, output_file="data/backtest_results.csv"):
    """
    バックテスト結果をCSVファイルに蓄積する関数。

    Args:
        result (dict): バックテスト結果（resultに格納されている情報）
        best_params (dict): ベストなパラメータ
        ticker_id (str): 対象銘柄ID
        ticker_name (str): 対象銘柄名
        interval (str): データのインターバル（例: "daily", "minute"）
        output_file (str): 結果を保存するCSVファイルのパス
    """
    # 実行日時を取得
    execution_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 保存するデータを作成
    data = {
        "実行日時": execution_time,
        "対象銘柄ID": ticker_id,
        "対象銘柄名": ticker_name,
        "データのインターバル": interval,
        **result,  # resultの内容を展開
        "ベストなパラメータ": str(best_params)  # 辞書を文字列として保存
    }

    # データをデータフレームに変換
    df = pd.DataFrame([data])

    # CSVファイルに追記（存在しない場合は新規作成）
    if not os.path.exists(output_file):
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
    else:
        df.to_csv(output_file, index=False, mode="a", header=False, encoding="utf-8-sig")

    print(f"バックテスト結果を {output_file} に保存しました！")

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
        self.buy_signals = []  # 買いシグナルを記録するリスト
        self.sell_signals = []  # 売りシグナルを記録するリスト

    def next(self):
        if crossover(self.smaS, self.smaL):
            self.buy()
            self.buy_signals.append(self.data.index[-1])  # 買いシグナルの日時を記録
        elif crossover(self.smaL, self.smaS):
            self.position.close()
            self.sell_signals.append(self.data.index[-1])  # 売りシグナルの日時を記録


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


######################################## main.py ########################################

import statistics
from typing import List, Tuple, Dict


def run_backtest_for_ticker(ticker: str, strategy_class) -> Tuple[Backtest, float, int, str, bool, bool, Dict]:
    """
    指定した銘柄でバックテストを実行し、結果を返す。

    Args:
        ticker (str): 銘柄コード
        strategy_class: 使用する戦略クラス

    Returns:
        Tuple[Backtest, float, int, str, bool, bool, Dict]: 
            Backtestオブジェクト、リターン、取引回数、戦略名、買いシグナルフラグ、売りシグナルフラグ、バックテスト結果
    """
    df = get_stock_data(ticker, drop_na=True)
    recent_data = filter_stock_data_by_period(df, days_ago=0, lookback_days=9999)

    # バックテストを実行
    bt, result, best_params, has_recent_buy_signal, has_recent_sell_signal, strategy_name = run_optimized_backtest(
        recent_data, strategy_class
    )

    return bt, result['Return [%]'], result['# Trades'], strategy_name, has_recent_buy_signal, has_recent_sell_signal, result


def display_results(
    returns: List[float],
    trade_counts: List[int],
    buy_signal_tickers: List[str],
    sell_signal_tickers: List[str],
    strategy_name: str,
    best_ticker: str,
    best_return: float,
    best_result: Dict,
):
    """
    バックテスト結果を表示する。

    Args:
        returns (List[float]): 各銘柄のリターン
        trade_counts (List[int]): 各銘柄の取引回数
        buy_signal_tickers (List[str]): 買いシグナルが出た銘柄
        sell_signal_tickers (List[str]): 売りシグナルが出た銘柄
        strategy_name (str): 使用した戦略名
        best_ticker (str): 最も利益が出た銘柄
        best_return (float): 最も利益が出た銘柄のリターン
        best_result (Dict): 最も利益が出た銘柄のバックテスト結果
    """
    # 平均リターンと平均取引回数を計算
    average_return = sum(returns) / len(returns) if returns else 0
    average_trade_count = sum(trade_counts) / len(trade_counts) if trade_counts else 0

    # リターンの標準偏差を計算
    return_std_dev = statistics.stdev(returns) if len(returns) > 1 else 0

    # 結果を表示
    print("\n複数銘柄バックテストの結果:")
    print(f"使用した戦略: {strategy_name}")
    print(f"平均リターン: {average_return:.2f}%")
    print(f"リターンの標準偏差: {return_std_dev:.2f}%")
    print(f"平均取引回数: {average_trade_count:.2f}")

    # 買いシグナルが出た銘柄を表示
    if buy_signal_tickers:
        print("\n直近2日間で買いシグナルが出た銘柄:")
        for ticker in buy_signal_tickers:
            print(f"- {ticker}")
    else:
        print("\n直近2日間で買いシグナルが出た銘柄はありません。")

    # 売りシグナルが出た銘柄を表示
    if sell_signal_tickers:
        print("\n直近2日間で売りシグナルが出た銘柄:")
        for ticker in sell_signal_tickers:
            print(f"- {ticker}")
    else:
        print("\n直近2日間で売りシグナルが出た銘柄はありません。")

    # 最も利益が出た銘柄を表示
    print("\n最も利益が出た銘柄:")
    print(f"銘柄: {best_ticker}")
    print(f"リターン: {best_return:.2f}%")
    print(f"バックテスト結果: {best_result}")


def main():
    """
    メイン処理を実行する。
    """
    # 銘柄リストを定義
    tickers = ["7011.T", ]
    # tickers = [
    # "7012.T", "7011.T", "6146.T", "6857.T", "7203.T", "8306.T", "5803.T", "2432.T", "8316.T", "8035.T",
    # "6758.T", "9983.T", "7013.T", "9984.T", "8411.T", "6501.T", "6098.T", "7974.T", "8136.T", "6861.T",
    # "6920.T", "9104.T", "7267.T", "4676.T", "8058.T", "8725.T", "8766.T", "4063.T", "9101.T", "9432.T",
    # "285A.T", "7182.T", "8001.T", "4502.T", "9749.T", "8031.T", "2914.T", "7741.T", "7936.T", "6702.T",
    # "6981.T", "5016.T", "6503.T", "6752.T", "6902.T", "6273.T", "9433.T", "9434.T", "6723.T", "4568.T",
    # "6954.T", "4755.T", "8630.T", "5401.T", "4751.T", "6367.T", "6532.T", "7751.T", "4661.T", "6701.T",
    # "8604.T", "8002.T", "7261.T", "7201.T", "4519.T", "8053.T", "6762.T", "8801.T", "9021.T", "8309.T",
    # "1605.T", "5108.T", "4543.T", "9020.T", "7735.T", "7003.T", "9107.T", "7270.T", "7269.T", "8802.T",
    # "8308.T", "4004.T", "9501.T", "5411.T", "6301.T", "6201.T", "7832.T", "5801.T", "8591.T", "4503.T",
    # "6526.T", "5406.T", "4901.T", "4578.T", "8750.T", "5838.T", "6594.T", "2502.T", "5802.T", "^N225"
    # ]

    # 使用する戦略クラス
    # strategy_class = SmaCross
    # strategy_class = RSICross
    # strategy_class = MACDCross
    # strategy_class = MaDeviationStrategy
    # strategy_class = BollingerBandStrategy
    # strategy_class = RsiStrategy
    # strategy_class = AtrTrailingStopStrategy
    # strategy_class = RSISignalStrategy

    # 以下うまくいかない
    strategy_class = RSIMACDStrategy

    # 結果を格納するリスト
    returns = []
    trade_counts = []
    buy_signal_tickers = []
    sell_signal_tickers = []

    # 最も利益が出た銘柄の情報を記録
    best_ticker = None
    best_return = float('-inf')
    best_result = None
    best_bt = None  # 最も利益が出たバックテストオブジェクト

    for ticker in tickers:
        bt, return_percentage, trade_count, strategy_name, has_recent_buy_signal, has_recent_sell_signal, result = run_backtest_for_ticker(
            ticker, strategy_class
        )

        # 結果をリストに追加
        returns.append(return_percentage)
        trade_counts.append(trade_count)

        # シグナルが出た銘柄をリストに追加
        if has_recent_buy_signal:
            buy_signal_tickers.append(ticker)
        if has_recent_sell_signal:
            sell_signal_tickers.append(ticker)

        # 最も利益が出た銘柄を更新
        if return_percentage > best_return:
            best_ticker = ticker
            best_return = return_percentage
            best_result = result
            best_bt = bt  # 最も利益が出たバックテストオブジェクトを記録

    # 結果を表示
    display_results(
        returns, trade_counts, buy_signal_tickers, sell_signal_tickers, strategy_name, best_ticker, best_return, best_result
    )

    # 最も利益が出たバックテスト結果をプロット
    if best_bt:  # Backtest オブジェクトが存在するか確認
        best_bt.plot(filename="backtest_result.html")
        print("\n最も利益が出たバックテスト結果を 'backtest_result.html' に保存しました！")
    else:
        print("\n最も利益が出たバックテスト結果をプロットできませんでした。")


if __name__ == "__main__":
    main()




