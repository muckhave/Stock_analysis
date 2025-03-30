
###### yahoo finance document  ：  https://yfinance-python.org/ ######

import yfinance as yf
import pandas as pd
import time
import os
from datetime import datetime

# 取得する期間を設定（例: "1y" -> 1年, "6mo" -> 6ヶ月, "5d" -> 5日）
PERIOD = "3y"

# 取得したい100銘柄 + 日経平均
tickers = [
    "7012.T", "7011.T", "6146.T", "6857.T", "7203.T", "8306.T", "5803.T", "2432.T", "8316.T", "8035.T",
    "6758.T", "9983.T", "7013.T", "9984.T", "8411.T", "6501.T", "6098.T", "7974.T", "8136.T", "6861.T",
    "6920.T", "9104.T", "7267.T", "4676.T", "8058.T", "8725.T", "8766.T", "4063.T", "9101.T", "9432.T",
    "285A.T", "7182.T", "8001.T", "4502.T", "9749.T", "8031.T", "2914.T", "7741.T", "7936.T", "6702.T",
    "6981.T", "5016.T", "6503.T", "6752.T", "6902.T", "6273.T", "9433.T", "9434.T", "6723.T", "4568.T",
    "6954.T", "4755.T", "8630.T", "5401.T", "4751.T", "6367.T", "6532.T", "7751.T", "4661.T", "6701.T",
    "8604.T", "8002.T", "7261.T", "7201.T", "4519.T", "8053.T", "6762.T", "8801.T", "9021.T", "8309.T",
    "1605.T", "5108.T", "4543.T", "9020.T", "7735.T", "7003.T", "9107.T", "7270.T", "7269.T", "8802.T",
    "8308.T", "4004.T", "9501.T", "5411.T", "6301.T", "6201.T", "7832.T", "5801.T", "8591.T", "4503.T",
    "6526.T", "5406.T", "4901.T", "4578.T", "8750.T", "5838.T", "6594.T", "2502.T", "5802.T", "^N225"
]

# 保存フォルダを data に変更
data_folder = "data/daily/"
os.makedirs(data_folder, exist_ok=True)
error_log_file = os.path.join(data_folder, "error_log.txt")

def log_error(message):
    """エラーログを記録する"""
    with open(error_log_file, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} - {message}\n")

def fetch_and_save_stock_data(ticker):
    try:
        # 期間を指定してデータ取得
        df = yf.download(ticker, period=PERIOD)
        if df.empty:
            log_error(f"{ticker} のデータが取得できませんでした。")
            return
        
        # ファイルパス（data フォルダに保存）
        file_path = os.path.join(data_folder, f"{ticker}.csv")
        
        # 既存データがあれば読み込んで結合（データ蓄積）
        if os.path.exists(file_path):
            old_df = pd.read_csv(file_path, index_col="Date", parse_dates=True)
            df = pd.concat([old_df, df])
            df = df[~df.index.duplicated(keep='last')]  # 重複データを削除
        
        # CSVに保存
        df.to_csv(file_path)
        print(f"{ticker} のデータを更新しました。")
    except Exception as e:
        log_error(f"{ticker} のデータ取得エラー: {str(e)}")

def main():
    for i, ticker in enumerate(tickers):
        print(f"[{i+1}/{len(tickers)}] {ticker} のデータを取得中...")
        fetch_and_save_stock_data(ticker)
        time.sleep(2)  # API制限対策（2秒間隔）
    print("すべての銘柄のデータ取得が完了しました。")

if __name__ == "__main__":
    main()
