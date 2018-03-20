from scipy import stats
import pandas as pd
import datetime
import sqlite3

import matplotlib.pyplot as plt
import matplotlib
matplotlib.rc('font', family='Malgun Gothic')

market_code = '0'
start_code = '004990'
end_code   = '999999'

start = pd.to_datetime('2017-03-01')
end = pd.to_datetime('2018-2-28')   # 365 days

period = 7  # duration of pct_change

con = sqlite3.connect("D:\SQLITEDB\koreaStock.db")
c = con.cursor()

# Get Index -------------------------------------------------------
market = "001"   # KOSPI

KOSPI = pd.read_sql("SELECT * from marketCandle where code='" + market + "'", con, index_col=["date"])

KOSPI.index = KOSPI.index.to_datetime()
KOSPI= KOSPI[(KOSPI.index >= start) & (KOSPI.index <= end)]
KOSPI.index.name = 'date'

KOSPI['Daily Return'] =KOSPI['close'].pct_change(1)
#--------------------------------------------------------------------

batch_codes = pd.read_sql("select code from stockCode where smarket = '" + market_code +\
                          "' and code >= '" + start_code + "' and code <= '" + end_code + "'\
                          order by code asc", con)['code'].tolist()
#code = "005930"   # 삼성전자
#code = "000020"   # 동화약품
#code = "005490"   #POSCO
#code = "000210"   #대림산업
#code = "005880"   #대한해운

for code in batch_codes:
    STOCK = pd.read_sql("SELECT * from dailyCandle where code='" + code + "'", con, index_col=["date"])

    STOCK.index = STOCK.index.to_datetime()
    STOCK = STOCK[(STOCK.index >= start) & (STOCK.index <= end)]
    STOCK.index.name = 'date'

    STOCK = STOCK[~STOCK.index.duplicated(keep='first')]  # remove duplicated data

    STOCK['Daily Return'] = STOCK['close'].pct_change(period)

    if STOCK.shape != KOSPI.shape:
        if STOCK.empty:
            print('code : {} DataFrame is empty!'.format(code))
        else:
            print('Shape of code {} is different from KOSPI shape'.format(code))
            print('Shape = ', STOCK.shape, ' vs. ', KOSPI.shape)
    else:
        beta,alpha,r_value,p_value,std_err = stats.linregress(KOSPI['Daily Return'].iloc[period:],STOCK['Daily Return'].iloc[period:])

        print("code= {}, beta= {}".format(code, beta))
        c.execute("UPDATE stockCode SET beta = {} WHERE code= '{}'".format(beta, code))

con.commit()

# plt.figure(1)
# KOSPI['Cumulative'] = KOSPI['close']/KOSPI['close'].iloc[0]
# STOCK['Cumulative'] = STOCK['close']/STOCK['close'].iloc[0]
# STOCK['Cumulative'].plot(label='stock')
# KOSPI['Cumulative'].plot(figsize=(10,8), label='KOSPI')
# plt.legend()
# plt.show()
#
# plt.figure(2)
# plt.scatter(STOCK['Daily Return'], KOSPI['Daily Return'], alpha=0.3)
# plt.show()
