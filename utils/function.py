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
