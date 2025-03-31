if __name__ == '__main__':
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

    from backtesting import Strategy
    from backtesting import Backtest
    from backtesting.lib import crossover
    from backtesting.test import SMA

    from utils.function import *
    from backtests.backtests import *


    ############### 以下メモ用 ################
    # get_stock_data(ticker)で株価データフレームを返す
    # get_stock_minute_data(ticker)で分足の株価データフレームを返す
    ##########################################

    ticker = "7203.T"
    df = get_stock_data(ticker)

    rdf , backtest_result,best_params = run_optimized_backtest(df,MACDCross)

    print(backtest_result)
    print(best_params)

    rdf.plot()