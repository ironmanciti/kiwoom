# -*- coding: utf-8 -*-
# 이동평균선 : sqlite db 혹은 키움 API 선택적 이용 가능

import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt

#------- start : 그래프 그릴때 공통으로 필요한 부분
import sqlite3
from datetime import datetime
import matplotlib.font_manager as fm

path = 'C:/windows/Fonts/gulim.ttc'
fontprop = fm.FontProperties(fname=path, size=18)

con = sqlite3.connect("D:\SQLITEDB\koreaStock.db")
cursor = con.cursor()

code = "005930"

# from SQLITE
#df  = pd.read_sql("SELECT * from dailyCandle where code='" + code + "'", con)

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

new_df = df[df['volume']!=0]

new_df.loc[:,'date'] = pd.to_datetime(new_df.loc[:,'date'])

new_df = new_df.set_index('date')
#------------- end : 그램프 data 사전 준비

# Moving average
ma5 = new_df['close'].rolling(window=5).mean()
ma20 = new_df['close'].rolling(window=20).mean()
ma60 = new_df['close'].rolling(window=60).mean()
ma120 = new_df['close'].rolling(window=120).mean()

# Insert columns
new_df.insert(len(new_df.columns), "MA5", ma5)
new_df.insert(len(new_df.columns), "MA20", ma20)
new_df.insert(len(new_df.columns), "MA60", ma60)
new_df.insert(len(new_df.columns), "MA120", ma120)

# Plot
plt.plot(new_df.index, new_df['close'], label='close')
plt.plot(new_df.index, new_df['MA5'], label='MA5')
plt.plot(new_df.index, new_df['MA20'], label='MA20')
plt.plot(new_df.index, new_df['MA60'], label='MA60')
plt.plot(new_df.index, new_df['MA120'], label='MA120')

plt.legend(loc="best")
plt.title("종목명 : " + codeName, fontproperties=fontprop)
plt.grid()
plt.show()
