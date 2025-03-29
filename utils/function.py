import pandas as pd
import os

def get_stock_data(ticker):
    # ファイルパスを作成
    file_path = os.path.join('data', f'{ticker}.T.csv')
    
    # CSVファイルが存在するか確認
    if os.path.exists(file_path):
        # CSVを読み込んでデータフレームに変換
        df = pd.read_csv(file_path)
        return df
    else:
        raise FileNotFoundError(f"{file_path} が見つかりません。")
