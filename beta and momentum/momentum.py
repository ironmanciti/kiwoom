#Momentum.py

import pandas as pd
import datetime
import dateutil.relativedelta
import sys
from functools import reduce

sys.path.append('../lib/')

from dbConnect import *
from matplotHangul import *

# market_code = '001' # KOSPI
start_code = '000000'
end_code   = '900000'

market_code = '201' # KOSPI200 / 만약 '001' 로 하면 KOPSI ANY 종목 대상
f_score = 7         # momentum 계산양을 줄이기 위해 KOSPI200 종목 중 F-SCORE 7 이상인 종목으로 대상 한정

period = 1  # duration of pct_change --> daily return 을 기준으로 beta 계산
input_invest_date = "2018-1-1"   # 투자 시작월
invest_date = datetime.datetime.strptime(input_invest_date, "%Y-%m-%d")

yymm = []
for i in range(12,0,-1):          # 투자 시작월에서 12 개월 이전 연,월 계산
    d1 = dateutil.relativedelta.relativedelta(months=i)
    yy = (invest_date - d1).year
    mm = (invest_date - d1).month
    yymm.append((yy,mm))

# KOSPI(001) 인 경우 ANY 종목 / KOSPI200 (201) 인 경우 stockcode 의 kospi200 = true 인 종목만 대상 --------
if market_code == '001':
    batch_codes = pd.read_sql("select code, code_name from stockcode where smarket = '" + market_code +\
                              "' and code >= '" + start_code + "' and code <= '" + end_code + "'\
                               and fscore >= %d order by code asc" % f_score, con=engine)
elif market_code == '201':
    batch_codes = pd.read_sql("select code, code_name from stockcode where kospi200 = true and fscore >= %d" \
                                % f_score, con=engine)
else:
    print("invalid market_code", market_code)
    quit()

momentum_data = []

# 대상 종목의 momentum 계산
for code, code_name in batch_codes[['code','code_name']].values:

    STOCK_ALL = pd.read_sql("SELECT * from dailycandle where code ='" + code + "'", con=engine, \
                                index_col=["date"])

    # 투자월(yymm[12][0] & yymm[12][1]) 직전 12 개월의 data 를 일봉 DB 에서 가져옴.
    STOCK_ALL.index = STOCK_ALL.index.to_datetime()
    STOCK_ALL = STOCK_ALL[(STOCK_ALL.index.year == yymm[0][0]) & (STOCK_ALL.index.month >= yymm[0][1]) | \
               (STOCK_ALL.index.year == yymm[11][0]) & (STOCK_ALL.index.month <= yymm[11][1])]
    STOCK_ALL.index.name = 'date'

    STOCK = STOCK_ALL[STOCK_ALL['code'] == code]     # 동일 연월의 다른 주식코드 제거 (Unique index 없을 경우)

    #STOCK = STOCK[~STOCK.index.duplicated(keep='first')]  # remove duplicated data
    start_close = STOCK.iloc[0].close   # yymm[0][0] 의 첫 record close value

    # 각 month 의 last day data 만 추출
    STOCK = STOCK[(pd.Series(STOCK.index.month) != pd.Series(STOCK.index.month).shift(-1)).values]

    momentum_row = [code, code_name, start_close]

    for yy, mm in yymm:
        momentum_row.append(STOCK.loc[(STOCK.index.year == yy) & (STOCK.index.month == mm)]['close'].values[0])

    STOCK['Gross Return'] = STOCK['close'].pct_change(1) + 1  # monthly Gross return

    STOCK.ix[0, 'Gross Return'] = (STOCK.ix[0, 'close'] - start_close) / start_close + 1

    STOCK_3M_Gross_Retun = STOCK['Gross Return'][-3:]
    STOCK_6M_Gross_Retun = STOCK['Gross Return'][-6:]
    STOCK_9M_Gross_Retun = STOCK['Gross Return'][-9:]
    STOCK_12M_Gross_Retun = STOCK['Gross Return'][-12:]

    momentum_row.append(reduce(lambda x, y: x*y, STOCK_3M_Gross_Retun.values))    # momentum = 각 월의 Gross Return 을 모두 곱함
    momentum_row.append(reduce(lambda x, y: x*y, STOCK_6M_Gross_Retun.values))
    momentum_row.append(reduce(lambda x, y: x*y, STOCK_9M_Gross_Retun.values))
    momentum_row.append(reduce(lambda x, y: x*y, STOCK_12M_Gross_Retun.values))

    column_label = ['code', 'name', 'start_close']
    for ym in yymm:
        column_label.append(str(ym))                # column_label 작성
    column_label.append('3mMtm')
    column_label.append('6mMtm')
    column_label.append('9mMtm')
    column_label.append('12mMtm')

    momentum_data.append(momentum_row)     # 완성된 row 를 전체 list 에 append

momentum_df = pd.DataFrame(momentum_data, columns=column_label)     # 전체 list 를 DataFrame 으로 변환

momentum_df.sort_values(['12mMtm'], ascending=False, inplace=True)

print(momentum_df.iloc[:5])
