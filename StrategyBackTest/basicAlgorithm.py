import zipline
import pandas_datareader.data as web
import matplotlib.pyplot as plt
import numpy as np
import sqlite3
from zipline.api import order_target_percent, symbol, record, set_commission, \
                        commission, schedule_function
from zipline.utils.factory import create_simulation_parameters
from zipline.algorithm import TradingAlgorithm
import pandas as pd
from datetime import datetime
from pandas import date_range
from zipline.utils.tradingcalendar import trading_day

import matplotlib
matplotlib.rc('font',family='Malgun Gothic')

#code = "005490" # backtest 할 종목
code_list = ["005490", "005930", "005880"]
start = datetime(2017, 7, 25)
end = datetime(2017, 7, 25)
# zipline 에 등록된 trading day 에 맞는 empty frame 생성
days = date_range(start, end, freq=trading_day)
data = pd.DataFrame(index=days)

for code in code_list:
    data[code] = np.nan
    df = web.DataReader("KRX:"+code, "google", start, end)
    df = df[['Close']]
    df.columns = [code]
    data[code] = df[code]
    data.fillna(method='ffill',inplace=True)

data = data.tz_localize("UTC")

# backtest using zipline
def initialize(context):
    # Reference to Sample Stocks
    #context.test = [symbol("005930"),symbol("005490"), symbol("005880")]
    context.sec = symbol("005930")
    #context.posco = symbol("005490")
    #context.daetong = symbol("005880")

    schedule_function(open_position)

    schedule_function(close_position)

    set_commission(commission.PerDollar(cost=0.00165)) # 0.165% commission

def open_position(context, data):
    order_target_percent(symbol("005930"), 0.1)

def close_position(context, data):
    order_target_percent(symbol("005930"), 0)

def handle_data(context, data):
    pass
    #test = data.current(context.test,"close")
    #test = data.is_stale(symbol("005930"))
    #if data.can_trade(symbol("005930")):
        #order_target_percent(symbol("005930"),1.0)
    # Position our portfolio optimization -> rebalance every minute
    #order_target_percent(context.sec, .27)
    #order_target_percent(context.posco, .20)
    #order_target_percent(context.daetong, .53)
    #price_history = data.history(context.test,fields="price",bar_count=5,\
    #                frequency='1d')
    #print(price_history)

lgo = TradingAlgorithm(sim_params=create_simulation_parameters(\
    capital_base=100000000), initialize=initialize, handle_data=handle_data)
result = algo.run(data)

# 종목 한글명
#con = sqlite3.connect("D:\SQLITEDB\koreaStock.db")
#cursor = con.cursor()

# 주어진 기간의 종가 chart
data.plot()
