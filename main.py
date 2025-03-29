import pandas as pd
import pandas_datareader.data as pdr
import matplotlib.pyplot as plt
import mplfinance as mpf
import datetime as dt
import talib as ta
import matplotlib.lines as mlines
import numpy as np
import requests
# from backtesting import Strategy
# from backtesting import Backtest
# from backtesting.lib import crossover
# from backtesting.test import SMA
# import yfinance as yf

import yfinance as yf

# 取得したい銘柄コード（例: トヨタ 7203.T）
ticker = "7203.T"

# Yahoo Finance から直近1年の日足データを取得
df = yf.download(ticker, period="1y")

# CSVに出力
df.to_csv(f"{ticker}_daily_1y.csv")

print(f"データを {ticker}_daily_1y.csv に保存しました。")