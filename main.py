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
# from backtesting import Strategy
# from backtesting import Backtest
# from backtesting.lib import crossover
# from backtesting.test import SMA

############### 以下メモ用 ################
# get_stock_data(ticker)で株価データフレームを返す
##########################################


ticker = "7203"
df = get_stock_data(ticker)

print(df)