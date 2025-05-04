

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
