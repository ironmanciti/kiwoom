#BettingAgainstBeta_monthlyBeta.py

from scipy import stats
import pandas as pd
import datetime
import dateutil.relativedelta
import sys

sys.path.append('../lib/')

from dbConnect import *
from matplotHangul import *

# market_code = '001' # KOSPI
start_code = '000000'
end_code   = '900000'

market_code = '201' # KOSPI200 을 beta 1 로 함 / 만약 '001' 로 하면 KOPSI ANY 종목 대상
f_score = 7         # beta vaue 계산양을 줄이기 위해 KOSPI200 종목 중 F-SCORE 7 이상인 종목으로 대상 한정

period = 1  # duration of pct_change --> daily return 을 기준으로 beta 계산
input_invest_date = "2017-04-01"   # 투자 시작월
invest_date = datetime.datetime.strptime(input_invest_date, "%Y-%m-%d")

yymm = []
for i in range(6, -1, -1):  # 투자 시작월에서 6 개월 이전 연,월 계산
    d1 = dateutil.relativedelta.relativedelta(months=i)
    yy = (invest_date - d1).year
    mm = (invest_date - d1).month
    yymm.append((yy,mm))

invest_ym = yymm[-1]        # 투자월 : yymm 의 마지막 연월

# Get Index : market = beta 1 --------  KOSPI / KOSPI200 ----------------------------
KOSPI = pd.read_sql("SELECT * from marketcandle where code='" + market_code + "'", con=engine, index_col=["date"])

KOSPI.index = KOSPI.index.to_datetime()
KOSPI= KOSPI[(KOSPI.index.year == yymm[0][0]) & (KOSPI.index.month >= yymm[0][1]) | \
             (KOSPI.index.year == yymm[6][0]) & (KOSPI.index.month <= yymm[6][1])]
KOSPI.index.name = 'date'

KOSPI['Daily Return'] = KOSPI['close'].pct_change(period)
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

beta_data = []

# 대상 종목의 beat 값 계산
for code, code_name in batch_codes[['code','code_name']].values:
    STOCK_ALL = pd.read_sql("SELECT * from dailycandle where code ='" + code + "'", con=engine, \
                                index_col=["date"])

    # 투자월(yymm[6][0] & yymm[6][1]) 직전 6 개월의 data 를 일봉 DB 에서 가져옴.
    STOCK_ALL.index = STOCK_ALL.index.to_datetime()
    STOCK_ALL = STOCK_ALL[(STOCK_ALL.index.year == yymm[0][0]) & (STOCK_ALL.index.month >= yymm[0][1]) | \
               (STOCK_ALL.index.year == yymm[6][0]) & (STOCK_ALL.index.month <= yymm[6][1])]
    STOCK_ALL.index.name = 'date'

    STOCK = STOCK_ALL[STOCK_ALL['code'] == code]     # 동일 연월의 다른 주식코드 제거 (Unique index 없을 경우)

    #STOCK = STOCK[~STOCK.index.duplicated(keep='first')]  # remove duplicated data

    STOCK['Daily Return'] = STOCK['close'].pct_change(period)   # daily return

    column_label = ['code', 'name']
    for ym in yymm:
        column_label.append(str(ym))                # column_label 작성
    column_label.append('6mAVG')

    if STOCK.shape != KOSPI.shape:
        if STOCK.empty:
            print('code : {} DataFrame is empty!'.format(code))
        else:
            print('Shape of code {} is different from KOSPI shape'.format(code))
            print('Shape = ', STOCK.shape, ' vs. ', KOSPI.shape)
    else:
        beta_value_row = [code, code_name]
        sum_6month = 0

        for yy, mm in yymm:
            M_KOSPI = KOSPI.loc[(KOSPI.index.year == yy) & (KOSPI.index.month == mm)]
            M_STOCK = STOCK.loc[(STOCK.index.year == yy) & (STOCK.index.month == mm)]

            beta,alpha,r_value,p_value,std_err = stats.linregress(M_KOSPI['Daily Return'].iloc[period:],\
                                                                  M_STOCK['Daily Return'].iloc[period:])
            if yy == invest_ym[0] and mm == invest_ym[1]:   # 투자하려는 월 제외
                pass
            else:
                sum_6month += beta           # 투자월 직전 6개월의 월별 beta 합산
            print("code= {}, YYMM = {}/{} beta= {}".format(code, yy, mm, beta))
            beta_value_row.append(beta)      # 월별 beta 를 한 row 에 append

        beta_value_row.append(sum_6month / 6)    # 6 개월 평균 beta 를 같은 row 에 append

        beta_data.append(beta_value_row)     # 완성된 row 를 전체 list 에 append

beta_df = pd.DataFrame(beta_data, columns=column_label)     # 전체 list 를 DataFrame 으로 변환

beta_df['Median'] = beta_df[str(invest_ym)].median()        # 투자하려는 월의 median 을 구함

df = beta_df[beta_df['6mAVG'] < beta_df['Median']][['code','name','6mAVG','Median']]
result = df.sort_values(['6mAVG'], ascending=False)

print('Long Strategy : top 5 of 6mAVG < Median')
print(result.iloc[:5],"\n")

df = beta_df[beta_df['6mAVG'] > beta_df['Median']][['code','name','6mAVG','Median']]
result = df.sort_values(['6mAVG'], ascending=True)

print('Short Strategy : top 5 of 6mAVG > Median')
print(result.iloc[:5])
