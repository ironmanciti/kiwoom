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

market_code = '201' # KOSPI200
f_score = 7

period = 1  # duration of pct_change
input_invest_date = "2017-08-01"
invest_date = datetime.datetime.strptime(input_invest_date, "%Y-%m-%d")
invest_year  = invest_date.year
invest_month = invest_date.month

d1 = dateutil.relativedelta.relativedelta(months=6)

beta_monthly_calc_start_date = invest_date - d1

start_year = end_year = beta_monthly_calc_start_date.year
start_month = beta_monthly_calc_start_date.month

yymm = []

if start_year == invest_year and start_month in [7,8,9,10,11,12]:
    end_year = start_year
    for m in range(invest_month - 6,invest_month):
        yymm.append((end_year, m))
else:
    end_year = start_year + 1
    for m in range(start_month, 13):
        yymm.append((start_year, m))
    for m in range(1, invest_month):
        yymm.append((end_year, m))

# Get Index -------------------------------------------------------
KOSPI = pd.read_sql("SELECT * from marketcandle where code='" + market_code + "'", con=engine, index_col=["date"])

KOSPI.index = KOSPI.index.to_datetime()
KOSPI= KOSPI[(KOSPI.index.year == yymm[0][0]) & (KOSPI.index.month >= yymm[0][1]) | \
             (KOSPI.index.year == yymm[5][0]) & (KOSPI.index.month <= yymm[5][1])]
KOSPI.index.name = 'date'

KOSPI['Daily Return'] = KOSPI['close'].pct_change(period)
#--------------------------------------------------------------------
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

for code, code_name in batch_codes[['code','code_name']].values:
    STOCK_ALL = pd.read_sql("SELECT * from dailycandle where code ='" + code + "'", con=engine, \
                                index_col=["date"])

    STOCK_ALL.index = STOCK_ALL.index.to_datetime()
    STOCK_ALL = STOCK_ALL[(STOCK_ALL.index.year == yymm[0][0]) & (STOCK_ALL.index.month >= yymm[0][1]) | \
               (STOCK_ALL.index.year == yymm[5][0]) & (STOCK_ALL.index.month <= yymm[5][1])]
    STOCK_ALL.index.name = 'date'

    STOCK = STOCK_ALL[STOCK_ALL['code'] == code]

    #STOCK = STOCK[~STOCK.index.duplicated(keep='first')]  # remove duplicated data

    STOCK['Daily Return'] = STOCK['close'].pct_change(period)

    month_label = ['code', 'name']
    for yy, mm in yymm:
        column_label.append(str(yy) + '/' + str(mm))
        if yy == invest_year and mm == invest_month:
            invest_column = str(yy) + '/' + str(mm)
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
            sum_6month += beta
            print("code= {}, YYMM = {}/{} beta= {}".format(code, yy, mm, beta))
            beta_value_row.append(beta)

        beta_value_row.append(sum_6month)

        beta_data.append(beta_value_row)

beta_df = pd.DataFrame(beta_data, columns=month_label)

beta_df['Median'] = beta_df[invest_column].median()
