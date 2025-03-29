import yfinance as yf
import pandas as pd
import time
import os
from datetime import datetime

# 取得したい50銘柄 + 日経平均
tickers = [
    "7203.T", "6758.T", "9984.T", "9433.T", "8306.T", "6861.T", "7974.T", "6954.T", "4689.T", "2768.T",
    "6098.T", "4568.T", "2413.T", "4578.T", "9101.T", "9104.T", "9107.T", "3407.T", "4502.T", "6301.T",
    "6367.T", "6501.T", "6503.T", "6902.T", "7733.T", "8035.T", "8058.T", "8766.T", "8802.T", "8830.T",
    "9020.T", "9021.T", "9202.T", "9301.T", "9432.T", "9735.T", "9766.T", "9983.T", "1928.T", "2432.T",
    "2802.T", "2897.T", "2914.T", "3382.T", "3861.T", "4151.T", "4503.T", "4565.T", "4751.T", "4901.T",
    "^N225"  # 日経平均
]

# 保存フォルダを data に変更
data_folder = "data"
os.makedirs(data_folder, exist_ok=True)
error_log_file = os.path.join(data_folder, "error_log.txt")

def log_error(message):
    """エラーログを記録する"""
    with open(error_log_file, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} - {message}\n")

# 1銘柄ずつデータ取得
def fetch_and_save_stock_data(ticker):
    try:
        # 直近1年の日足データ取得
        df = yf.download(ticker, period="1y")
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

# メイン処理
def main():
    for i, ticker in enumerate(tickers):
        print(f"[{i+1}/{len(tickers)}] {ticker} のデータを取得中...")
        fetch_and_save_stock_data(ticker)
        time.sleep(2)  # API制限対策（2秒間隔）
    print("すべての銘柄のデータ取得が完了しました。")

if __name__ == "__main__":
    main()
