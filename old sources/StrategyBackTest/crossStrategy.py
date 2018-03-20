import zipline
import pandas_datareader.data as web
import matplotlib.pyplot as plt
import numpy as np
import sqlite3

from zipline.api import order_target, record, symbol, set_commission, commission
from zipline.utils.factory import create_simulation_parameters
from zipline.algorithm import TradingAlgorithm
import pandas as pd
from datetime import datetime
from zipline.utils.tradingcalendar import trading_day
from pandas import date_range
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import matplotlib
matplotlib.rc('font',family='Malgun Gothic')

code = "005490" # backtest 할 종목
start = datetime(2017, 1, 1)
end = datetime(2017, 12, 31)
p_short = 5
p_long = 25

# zipline 에 등록된 trading day 에 맞는 empty frame 생성
days = date_range(start, end, freq=trading_day)
data = pd.DataFrame(index=days)
data[code] = np.nan

# 종목 한글명
con = sqlite3.connect("D:\SQLITEDB\koreaStock.db")
cursor = con.cursor()

cursor.execute("SELECT code_name from stockCode where code='" + code + "'")
for row in cursor:
    codeName = row[0]  # 종목 한글명

# from SQLITE
#df  = pd.read_sql("SELECT * from dailyCandle where code='" + code + "'", con)

# from kiwoom API
from kiwoomMain import *
app = QApplication(sys.argv)
kiwoom = Kiwoom()
kiwoom.comm_connect()

dict = kiwoom.dailyCandle(code)
df = pd.DataFrame.from_dict(dict)

new_df = df[df['volume']!=0]

new_df.loc[:,'date'] = pd.to_datetime(new_df.loc[:,'date'])

new_df = new_df[(new_df['date'] >= start) & (new_df['date'] <= end)]

new_df.set_index('date', inplace=True)
new_df = new_df[['close']]
new_df.columns = [code]

# kiwoom/DB 에서 가져온 df의 종가를 trading day empty frame 에 update
data[code] = new_df[code]
data.fillna(method='ffill',inplace=True) # 국내 시장 date 없는 날은 전일 종가로 채움
data.sort_index(inplace=True)
data = data.tz_localize("UTC")

# backtest using zipline
def initialize(context):
    context.i = 0
    context.sym = symbol(code)
    context.hold = False

    set_commission(commission.PerDollar(cost=0.00165)) # 0.165% commission

def handle_data(context, data):
    context.i += 1
    if context.i < p_long:
        return

    buy = False
    sell = False

    ma_short = data.history(context.sym, 'price', p_short, '1d').mean()
    ma_long = data.history(context.sym, 'price', p_long, '1d').mean()

    if ma_short > ma_long and context.hold == False:
        order_target(context.sym, 100)
        context.hold = True
        buy = True
    elif ma_short < ma_long and context.hold == True:
        order_target(context.sym, -100)
        context.hold = False
        sell = True

    record(AAPL=data.current(context.sym, "price"), ma_short=ma_short, \
           ma_long=ma_long, buy=buy, sell=sell)

algo = TradingAlgorithm(sim_params=create_simulation_parameters(\
    capital_base=100000000), initialize=initialize, handle_data=handle_data)
result = algo.run(data)

# matplotlib 한글 처리
import matplotlib.font_manager as fm
path = 'C:/windows/Fonts/gulim.ttc'
fontprop = fm.FontProperties(fname=path, size=18)
# 주어진 기간의 종가 chart
plt.figure(1)
plt.plot(data.index, data[code])
plt.title(codeName, fontproperties=fontprop)

plt.plot(result.index, result.ma_short)
plt.plot(result.index, result.ma_long)

plt.plot(result.ix[result.buy == True].index, result.ma_short[result.buy == True], '^')
plt.plot(result.ix[result.sell == True].index, result.ma_short[result.sell == True], 'v')

plt.legend(loc='best')
plt.legend()
plt.show()
# 전략에 따른 backtest 기간 중 portfolio value
plt.figure(2)
plt.plot(result.index, result.portfolio_value)
plt.title("backtest 기간 중 portfolio value")
plt.show()

print(result[['starting_cash','ending_cash','ending_value']])
