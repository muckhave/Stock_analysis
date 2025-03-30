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
from utils.function import get_stock_data
from yahoo_finance_api2 import share
from yahoo_finance_api2.exceptions import YahooFinanceError
import pandas as pd


import requests
import json

import requests
import pandas as pd

# 取得したい銘柄コード
symbol = "1379.T"
interval = "5m"  # 5分足
range_period = "60d"  # 60日分

# Yahoo!ファイナンスのAPIエンドポイント
url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={interval}&range={range_period}"

# User-Agentを設定
headers = {"User-Agent": "Mozilla/5.0"}

# APIリクエストを送信
response = requests.get(url, headers=headers)
data = response.json()

# 必要なデータを取得
chart = data["chart"]["result"][0]
timestamps = chart["timestamp"]
ohlc = chart["indicators"]["quote"][0]

# DataFrameに変換
df = pd.DataFrame({
    "timestamp": pd.to_datetime(timestamps, unit="s"),  # UNIX時間を日時に変換
    "open": ohlc["open"],
    "high": ohlc["high"],
    "low": ohlc["low"],
    "close": ohlc["close"],
    "volume": ohlc["volume"]
})

# 結果を確認
print(df.head())

# CSVに保存
df.to_csv("stock_data_1379.csv", index=False)
