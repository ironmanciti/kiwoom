# -*- coding: utf-8 -*-
# 두개 종목의 주가를 비교

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.finance as matfin
import matplotlib.ticker as ticker

#------- start : 그래프 그릴때 공통으로 필요한 부분
import sqlite3
from datetime import datetime
import matplotlib.font_manager as fm

path = 'C:/windows/Fonts/gulim.ttc'
fontprop = fm.FontProperties(fname=path, size=18)

con = sqlite3.connect("D:\SQLITEDB\koreaStock.db")
cursor = con.cursor()

code = "005930"

start = datetime(2016,3,1)
end   = datetime(2016,3,31)

# from kiwoom API
from kiwoomMain import *
app = QApplication(sys.argv)
kiwoom = Kiwoom()
kiwoom.comm_connect()

dict = kiwoom.dailyCandle(code)
df = pd.DataFrame.from_dict(dict)

cursor.execute("SELECT code_name from stockCode where code='" + code + "'")
for row in cursor:
    codeName = row[0]

df = df[df['volume'] > 0]
df.loc[:,'date'] = pd.to_datetime(df.loc[:,'date'])

df = df[(df['date'] >= start) & (df['date'] <= end)]

df.set_index('date', inplace=True)
df.sort_index(inplace=True)

fig = plt.figure(figsize=(12,8))
ax = fig.add_subplot(111)

day_list = []
name_list = []

for i, day in enumerate(df.index):
    if day.dayofweek == 0:
        day_list.append(i)
        name_list.append(day.strftime('%Y-%m-%d') + '(Mon)')

ax.xaxis.set_major_locator(ticker.FixedLocator(day_list))
ax.xaxis.set_major_formatter(ticker.FixedFormatter(name_list))

matfin.candlestick2_ohlc(ax, df['open'], df['high'], df['low'], df['close'],\
    width=0.5, colorup='r', colordown='b')
plt.grid()
plt.show()
