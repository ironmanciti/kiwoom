import pandas as pd
import matplotlib.pyplot as plt

#------- start : 그래프 그릴때 공통으로 필요한 부분
from datetime import datetime
import matplotlib
matplotlib.rc('font', family='Malgun Gothic')

from dbConnect import *

code_list = ["001", "201"]

stocks = []
codeNames = []
for code in code_list:

    df  = pd.read_sql("SELECT * from marketcandle where code='" + code + "'", conn)
    df.loc[:,'date'] = pd.to_datetime(df.loc[:,'date'])
    df.set_index('date', inplace=True)

    if code == "001":
        codeNames.append("종합주가지수")
    elif code == "201":
        codeNames.append("KOSPI200")
        start_index = df.index[0]

    stocks.append(df)

for i in range(len(stocks)):
    stocks[i] = stocks[i][stocks[i].index >= start_index]
    stocks[i]['Normed Price'] = stocks[i]['close'] * 100 / stocks[i]['close'][0]

plt.plot(stocks[0].index,stocks[0]['Normed Price'], label=codeNames[0])
plt.plot(stocks[1].index,stocks[1]['Normed Price'], label=codeNames[1])
plt.legend(loc="best")
plt.title("종목명 : " + codeNames[0] + " / " + codeNames[1])
plt.grid()
plt.show()
