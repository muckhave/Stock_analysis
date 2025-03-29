import pandas as pd
import os

def get_stock_data(ticker):
    file_path = os.path.join("data", f"{ticker}.T.csv")
    
    # CSVを適切に読み込む
    df = pd.read_csv(file_path, skiprows=2, index_col=0, parse_dates=True)
    
    # 列名の順番を指定して設定
    df.columns = ["Close", "High", "Low", "Open", "Volume"]
    
    # インデックス（Date）を日付に変換
    df.index = pd.to_datetime(df.index)
    
    return df