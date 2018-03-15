
# 월별 beta 와 market median beta 비교
import numpy as np
import pandas as pd
#import pandas_datareader.data as web
import matplotlib.pyplot as plt

from sqlalchemy import create_engine
engine = create_engine("mysql+pymysql://yjoh:1234@localhost/stockdb?charset=utf8",convert_unicode=True)
conn = engine.connect()

#------- start : 그래프 그릴때 공통으로 필요한 부분
from datetime import datetime
import matplotlib.font_manager as fm
import matplotlib
matplotlib.rc('font', family='Malgun Gothic')
path = 'C:/windows/Fonts/gulim.ttc'
fontprop = fm.FontProperties(fname=path, size=18)

from BettingAgainstBeta_mdedian import *

file = "\\betatestMonday 12. March 2018.csv"

market_code = '001'
if market_code == '001':
    index_name = 'KOSPI'
elif market_code == '101':
    index_name = 'KOSDAQ'

#code = "005930"  # STOCK to compare
code = "000020"  # STOCK to compare
start_date = '2016-6-1'
end_date   = '2017-5-31'

code_name = pd.read_sql("SELECT code_name from stockcode where code='" + code + "'", con=engine)

market_candle = pd.read_sql("SELECT * from marketcandle where code ='" + market_code + "' and date >= '" + start_date + "' and date <= '" + end_date + "'", con=engine)
market_candle['normal close'] = market_candle['close'] * 100 / market_candle['close'][0]

STOCK_candle = pd.read_sql("SELECT * from dailycandle where code ='" + code + "' and date >= '" + start_date + "' and date <= '" + end_date + "'", con=engine)
STOCK_candle['normal close'] = STOCK_candle['close'] * 100 / STOCK_candle['close'][0]

col, median, df = get_median(start_date, file)
#monthly_beta = df[df['code'] == 20]

market_candle['normal close'].plot(label='KOSPI', figsize=(16,8), title='Beta Compare')
STOCK_candle['normal close'].plot(label=code_name.values[0][0])
#monthly_beta.plot(kind='bar',label=code_name.values[0][0])

plt.legend(loc='best')
plt.show()
