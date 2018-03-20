from zipline.api import order_target_percent, symbol, record, set_commission, \
                        commission, schedule_function
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

from zipline.api import order_target, record, symbol

code_list = ["KRX:005930", "KRX:005490"]
symbol_list = ['AAPL', 'GOOGL']
start = datetime(2010, 7, 25)
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
data.columns = [symbol_list]

def initialize(context):
    context.i = 0
    context.asset = symbol(symbol_list[0])
    
    set_commission(commission.PerDollar(cost=0.00165)) # 0.165% commission


def handle_data(context, data):
   #skip first 300 days to get full windows
    context.i += 1
    if context.i < 300:
        return
    
    #compute average
    sh_ma = data.history(context.asset, 'price', bar_count=100, frequency='1d').mean()
    lg_ma  = data.history(context.asset, 'price', bar_count=300, frequency='1d').mean()
    
    if sh_ma > lg_ma:
        order_target(context.asset, 100)
    elif sh_ma < lg_ma:
        order_target(context.asset, 0)
        
    record(AAPL=data.current(context.asset, 'price'),
              short_mvag = sh_ma,
              long_mvag = lg_ma)
    
algo = TradingAlgorithm(sim_params=create_simulation_parameters(\
    capital_base=100000000), initialize=initialize, handle_data=handle_data)
perf = algo.run(data)

# 종목 한글명
con = sqlite3.connect("D:\SQLITEDB\koreaStock.db")
cursor = con.cursor()
cursor.execute("SELECT code_name from stockCode where code='" + code[4:] + "'")
for row in cursor:
    codeName = row[0]  # 종목 한글명    

fig = plt.figure(figsize=(12,8))
ax1 = fig.add_subplot(211)
perf.portfolio_value.plot(ax=ax1)
ax1.set_ylabel('portfolio value in $')

ax2 = fig.add_subplot(212)
perf['AAPL'].plot(ax=ax2, label=codeName)
perf[['short_mvag', 'long_mvag']].plot(ax=ax2)

perf_trans = perf.iloc[[t != [] for t in perf.transactions]]
buys = perf_trans.ix[[t[0]['amount'] > 0 for t in perf_trans.transactions]]
sells =  perf_trans.ix[[t[0]['amount'] < 0 for t in perf_trans.transactions]]
ax2.plot(buys.index, perf.short_mvag.ix[buys.index], '^', markersize=10, color='m')
ax2.plot(sells.index, perf.short_mvag.ix[sells.index], 'v', markersize=10, color='k')
ax2.set_ylabel('price in $')
plt.legend(loc=0)
plt.show()