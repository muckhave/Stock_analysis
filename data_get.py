
###### yahoo finance document  ：  https://yfinance-python.org/ ######

import yfinance as yf
import pandas as pd
import time
import os
from datetime import datetime

# 取得する期間を設定（例: "1y" -> 1年, "6mo" -> 6ヶ月, "5d" -> 5日）
PERIOD = "5y"

# 取得したい100銘柄 + 日経平均
# tickers = [
#     "7012.T", "7011.T", "6146.T", "6857.T", "7203.T", "8306.T", "5803.T", "2432.T", "8316.T", "8035.T",
#     "6758.T", "9983.T", "7013.T", "9984.T", "8411.T", "6501.T", "6098.T", "7974.T", "8136.T", "6861.T",
#     "6920.T", "9104.T", "7267.T", "4676.T", "8058.T", "8725.T", "8766.T", "4063.T", "9101.T", "9432.T",
#     "285A.T", "7182.T", "8001.T", "4502.T", "9749.T", "8031.T", "2914.T", "7741.T", "7936.T", "6702.T",
#     "6981.T", "5016.T", "6503.T", "6752.T", "6902.T", "6273.T", "9433.T", "9434.T", "6723.T", "4568.T",
#     "6954.T", "4755.T", "8630.T", "5401.T", "4751.T", "6367.T", "6532.T", "7751.T", "4661.T", "6701.T",
#     "8604.T", "8002.T", "7261.T", "7201.T", "4519.T", "8053.T", "6762.T", "8801.T", "9021.T", "8309.T",
#     "1605.T", "5108.T", "4543.T", "9020.T", "7735.T", "7003.T", "9107.T", "7270.T", "7269.T", "8802.T",
#     "8308.T", "4004.T", "9501.T", "5411.T", "6301.T", "6201.T", "7832.T", "5801.T", "8591.T", "4503.T",
#     "6526.T", "5406.T", "4901.T", "4578.T", "8750.T", "5838.T", "6594.T", "2502.T", "5802.T", "^N225"
# ]

tickers = [
    "7012.T", "7011.T", "6146.T",
]

# データ保存フォルダ
data_folder = "data/daily/"
os.makedirs(data_folder, exist_ok=True)
error_log_file = os.path.join(data_folder, "error_log.txt")

def log_error(message):
    """エラーログを記録する"""
    with open(error_log_file, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} - {message}\n")

def read_existing_data(file_path):
    """既存のCSVデータを読み込む（ヘッダー処理 & 日付型修正）"""
    try:
        df = pd.read_csv(file_path, index_col=0, parse_dates=True)  # `Date` をインデックスとして読み込む
        df.index = pd.to_datetime(df.index)  # **ここで明示的に日付型に変換**
        return df
    except Exception as e:
        log_error(f"{file_path} の読み込みエラー: {str(e)}")
        return pd.DataFrame()  # 空のデータフレームを返す

def fetch_and_save_stock_data(ticker):
    try:
        df = yf.download(ticker, period=PERIOD)

        if df.empty:
            log_error(f"{ticker} のデータが取得できませんでした。")
            return

        df.index = pd.to_datetime(df.index)  # **取得データも日付型に変換**
        file_path = os.path.join(data_folder, f"{ticker}.csv")

        if os.path.exists(file_path):
            old_df = read_existing_data(file_path)

            # **既存データの日付も `Timestamp` 型に統一**
            old_df.index = pd.to_datetime(old_df.index)

            # **データ統合 & 重複削除**
            df = pd.concat([old_df, df])
            df = df.sort_index()
            df = df.loc[~df.index.duplicated(keep='last')]  # **重複削除を適用**

        df.to_csv(file_path, index=True)
        print(f"✅ ファイル {file_path} にデータを保存しました。")

    except Exception as e:
        log_error(f"{ticker} のデータ取得エラー: {str(e)}")

def main():
    print("スクリプトが実行されました。")
    for i, ticker in enumerate(tickers):
        print(f"[{i+1}/{len(tickers)}] {ticker} のデータを取得中...")
        fetch_and_save_stock_data(ticker)
        time.sleep(2)
    print("すべての銘柄のデータ取得が完了しました。")

if __name__ == "__main__":
    print("スクリプト開始")
    main()