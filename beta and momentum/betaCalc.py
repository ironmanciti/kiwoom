from scipy import stats
import pandas as pd
import datetime
import sys
sys.path.append('../lib/')

from dbConnect import *

import matplotlib.pyplot as plt
import matplotlib
matplotlib.rc('font', family='Malgun Gothic')

start = pd.to_datetime('2017-03-01')
end = pd.to_datetime('2018-2-28')

period = 1  # duration of pct_change

# Get Index -------------------------------------------------------
market = "201"   # KOSPI200

KOSPI200 = pd.read_sql("SELECT * from marketcandle where code='" + market + "'", con, index_col=["date"])

KOSPI200.index = KOSPI200.index.to_datetime()
KOSPI200 = KOSPI200[(KOSPI200.index >= start) & (KOSPI200.index <= end)]
KOSPI200.index.name = 'date'

KOSPI200['Daily Return'] = KOSPI200['close'].pct_change(period)
#--------------------------------------------------------------------

batch_codes = pd.read_sql("select code from stockcode where kospi200 = true", conn)['code'].tolist()

try:
    sql = "ALTER TABLE stockcode ADD beta FLOAT NOT NULL AFTER kospi200"
    cursor.execute(sql)
except:
    print("beta not added")

for code in batch_codes:
    df = pd.read_sql("SELECT * from dailycandle where code ='" + code + "'", conn, index_col=["date"])

    df.index = df.index.to_datetime()
    df = df[(df.index >= start) & (df.index <= end)]
    df.index.name = 'date'

    df = df[~df.index.duplicated(keep='first')]  # remove duplicated data if there is

    df['Daily Return'] = df['close'].pct_change(period)

    if df.shape != KOSPI200.shape:
        if df.empty:
            print('code : {} DataFrame is empty!'.format(code))
        else:
            print('Shape of code {} is different from KOSPI200 shape'.format(code))
            print('Shape = ', df.shape, ' vs. ', KOSPI200.shape)
    else:
        beta,alpha,r_value,p_value,std_err = stats.linregress(KOSPI200['Daily Return'].iloc[period:], \
                                            df['Daily Return'].iloc[period:])

        print("code= {}, beta= {}".format(code, beta))
        sql = "UPDATE stockCode SET beta = {} WHERE code= '{}'".format(beta, code)
        cursor.execute(sql)

con.commit()
