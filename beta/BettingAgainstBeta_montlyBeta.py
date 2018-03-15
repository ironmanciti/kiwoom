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
input_invest_date = "2017-04-01"
invest_date = datetime.datetime.strptime(input_invest_date, "%Y-%m-%d")

yymm = []
for i in range(6, -1, -1):
    d1 = dateutil.relativedelta.relativedelta(months=i)
    yy = (invest_date - d1).year
    mm = (invest_date - d1).month
    yymm.append((yy,mm))

invest_ym = yymm[-1]

# Get Index -------------------------------------------------------
KOSPI = pd.read_sql("SELECT * from marketcandle where code='" + market_code + "'", con=engine, index_col=["date"])

KOSPI.index = KOSPI.index.to_datetime()
KOSPI= KOSPI[(KOSPI.index.year == yymm[0][0]) & (KOSPI.index.month >= yymm[0][1]) | \
             (KOSPI.index.year == yymm[6][0]) & (KOSPI.index.month <= yymm[6][1])]
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
               (STOCK_ALL.index.year == yymm[6][0]) & (STOCK_ALL.index.month <= yymm[6][1])]
    STOCK_ALL.index.name = 'date'

    STOCK = STOCK_ALL[STOCK_ALL['code'] == code]

    #STOCK = STOCK[~STOCK.index.duplicated(keep='first')]  # remove duplicated data

    STOCK['Daily Return'] = STOCK['close'].pct_change(period)

    column_label = ['code', 'name']
    for ym in yymm:
        column_label.append(str(ym))
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
            if yy == invest_ym[0] and mm == invest_ym[1]:
                pass
            else:
                sum_6month += beta
            print("code= {}, YYMM = {}/{} beta= {}".format(code, yy, mm, beta))
            beta_value_row.append(beta)

        beta_value_row.append(sum_6month / 6)

        beta_data.append(beta_value_row)

beta_df = pd.DataFrame(beta_data, columns=column_label)

beta_df['Median'] = beta_df[str(invest_ym)].median()
