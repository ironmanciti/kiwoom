# -*- coding: utf-8 -*-
# 두개 종목의 주가를 비교

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

code_list = ["005930", "066570"]

# from kiwoom API
# from kiwoomMain import *

stocks = []
codeNames = []
for code in code_list:

    df  = pd.read_sql("SELECT * from dailyCandle where code='" + code + "'", con)

    cursor.execute("SELECT code_name from stockCode where code='" + code + "'")
    for row in cursor:
        codeNames.append(row[0])

    df.loc[:,'date'] = pd.to_datetime(df.loc[:,'date'])
    df.set_index('date', inplace=True)

    stocks.append(df)

plt.plot(stocks[0].index,stocks[0]['close'], label='Samsung')
plt.plot(stocks[1].index,stocks[1]['close'], label='LG')
plt.legend(loc="best")
plt.title("종목명 : " + codeNames[0] + " / " + codeNames[1], fontproperties=fontprop)
plt.grid()
plt.show()
