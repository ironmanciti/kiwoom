# -*- coding: utf-8 -*-
# 두개 종목의 주가를 비교

import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt

#------- start : 그래프 그릴때 공통으로 필요한 부분
import sqlite3
from datetime import datetime
import matplotlib.font_manager as fm
import matplotlib
matplotlib.rc('font', family='Malgun Gothic')

path = 'C:/windows/Fonts/gulim.ttc'
fontprop = fm.FontProperties(fname=path, size=18)

con = sqlite3.connect("D:\SQLITEDB\koreaStock.db")
cursor = con.cursor()

code = "005930"

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

df.loc[:,'date'] = pd.to_datetime(df.loc[:,'date'])
df.set_index('date', inplace=True)

fig = plt.figure(figsize=(12,8))
top_axes = plt.subplot2grid((4,4), (0,0), rowspan=3, colspan=4)
bottom_axes = plt.subplot2grid((4,4), (3,0), rowspan=1, colspan=4)
bottom_axes.get_yaxis().get_major_formatter().set_scientific(False)

top_axes.plot(df.index, df['close'], label='Samsung Electronics')
bottom_axes.plot(df.index, df['volume'])

plt.title("종목명 : " + codeName)
# plt.title("종목명 : " + codeName, fontproperties=fontprop)
plt.tight_layout()
plt.show()
