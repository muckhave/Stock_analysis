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

close = df["Close"]

# 移動平均
df['ma5'], df['ma25'] = ta.SMA(close ,timeperiod=5), ta.SMA(close ,timeperiod=25)

# RSI
rsi14 = ta.RSI(close, timeperiod=14)
rsi28 = ta.RSI(close, timeperiod=28)
df['rsi14'], df['rsi28'] = rsi14, rsi28

# 補助線
df['70'] = [70 for _ in close] # 買われすぎの目安
df['30'] = [30 for _ in close] # 売られすぎの目安

rdf = df[dt.datetime(2024,3,28):dt.datetime(2025,3,28)]

apd  = {
          # 5日移動平均線
          "MA5": mpf.make_addplot(rdf['ma5'], color='blue',
                                panel=0, width=0.7),
          # 25日移動平均線
          "MA25": mpf.make_addplot(rdf['ma25'], color='green',
                                panel=0, width=0.7),
          # RSI 14
          "RSI14": mpf.make_addplot(rdf['rsi14'], color='red',
                                panel=1, width=0.7),
          # RSI 28
          "RSI28": mpf.make_addplot(rdf['rsi28'], color='blue',
                                panel=1, width=0.7),
          # 補助線
          "70": mpf.make_addplot(rdf['70'], color='green',
                                panel=1, width=0.7),
          "30": mpf.make_addplot(rdf['30'], color='green',
                                panel=1, width=0.7)
      }

fig, axes = mpf.plot(rdf, type="candle", figratio=(2,1),
                     addplot=list(apd.values()), returnfig=True)
#axes[0].legend([None]*(len(apd)+2))
#handles = axes[0].get_legend().legendHandles
#axes[0].legend(handles=handles[2:4], labels=list(apd.keys()))
handles = [
    mlines.Line2D([], [], color=value["color"], label=key)
    for key, value in apd.items()
    if value["panel"] == 0
]
axes[0].legend(handles=handles, loc="best", frameon=False, fontsize=10)
axes[2].legend(["RSI14", "RSI28"])
plt.show()