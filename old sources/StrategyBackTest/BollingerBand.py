from zipline.api import order_target_percent, symbol, record, set_commission, \
                        commission
from zipline.utils.factory import create_simulation_parameters
from zipline.algorithm import TradingAlgorithm
from datetime import datetime
from pandas import date_range
from zipline.utils.tradingcalendar import trading_day
import pandas as pd
import numpy as np
import sqlite3
import pandas_datareader.data as web

import matplotlib.pyplot as plt
import matplotlib
matplotlib.rc('font',family='Malgun Gothic')

code_list = ["KRX:010140"]
symbol_list = ['AAPL']
start = datetime(2010, 1, 1)
end = datetime(2018, 1, 1)
# zipline 에 등록된 trading day 에 맞는 empty frame 생성
days = date_range(start, end, freq=trading_day)
data = pd.DataFrame(index=days)

for code in code_list:
    data[code] = np.nan
    df = web.DataReader(code, "google", start, end)
    df = df[['Close']]
    df.columns = [code]
    data[code] = df[code]
    data.fillna(method='ffill',inplace=True)

data = data.tz_localize("UTC")
data.columns = [symbol_list]

def initialize(context):
    context.i = 0
    context.upper = False
    context.lower = False

    context.S1   = symbol(symbol_list[0])

    set_commission(commission.PerDollar(cost=0.00165)) # 0.165% commission


def handle_data(context, data):
    context.i += 1
    if context.i < 50:
        return

    S1 = context.S1
    buy = False
    sell = False

    cur_price = data.current(S1, 'price')
    prices = data.history(S1, 'price', 20, '1d')

    ma_20 = prices.mean()
    std = prices.std()
    upper_band = ma_20 + 2*std
    lower_band = ma_20 - 2*std

    if cur_price > upper_band and context.upper == False:
        order_target_percent(S1, -1.0)
        sell = True
        context.upper = True
        context.lower = False
        print("Shorting: upper {}, cur {}".format(upper_band, cur_price))
    elif cur_price < lower_band and context.lower == False:
        order_target_percent(S1, 1.0)
        buy = True
        context.lower = True
        context.upper = False
        print("BUYing: lower {}, cur {}".format(lower_band, cur_price))

    record(S1=S1,
           upper_band=upper_band,
           lower_band=lower_band,
           ma_20=ma_20,
           price=cur_price,
           buy=buy,
           sell=sell)

algo = TradingAlgorithm(sim_params=create_simulation_parameters(\
    capital_base=100000000), initialize=initialize, handle_data=handle_data)
result = algo.run(data)


# 종목 한글명  
con = sqlite3.connect("D:\SQLITEDB\koreaStock.db")
cursor = con.cursor()
  
cursor.execute("SELECT code_name from stockCode where code='" + code[4:] + "'")
for row in cursor:
    codeName = row[0]  
# 주어진 기간의 종가 chart
plt.figure(1)
plt.plot(result.index, result.price)
plt.title(codeName)

plt.plot(result.index, result.upper_band)
plt.plot(result.index, result.lower_band)

plt.legend(loc='best')
plt.legend()
plt.show()
# 전략에 따른 backtest 기간 중 portfolio value
plt.figure(2)
plt.plot(result.index, result.portfolio_value)
plt.title("backtest 기간 중 portfolio value")
plt.show()

print(result[['starting_value','ending_value']])
