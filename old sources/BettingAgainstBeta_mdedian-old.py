#BettingAgainstBeta_median.py

import pandas as pd
import datetime
import os

def get_column_name(yymm):
    ym = pd.to_datetime(yymm)
    yy = ym.year
    mm = ym.month
    col_name = str(yy) + '/' + str(mm)
    return col_name

def average_prev6_beta(start_month, df):
    start = start_month
    start = pd.to_datetime(start)
    start_year = start.year
    start_month = start.month
    yymm = []
    if start.month in [1,2,3,4,5,6,7]:
        end_year = start_year
        for m in range(start.month, start.month + 6):
            yymm.append((end_year, m))
    else:
        for m in range(start.month, 13):
            yymm.append((start_year,m))
        end_year = start_year + 1
        for m in range(1, start_month-6):
            yymm.append((end_year,m))

    month_label = []
    for yy, mm in yymm:
        month_label.append(str(yy) + '/' + str(mm))

    tot = 0
    for col in month_label:
        tot += df[col].values[0]

    average = tot / 6

    return average

def get_median(code, yyyymm, start_month, file):    #yyyymm = '2016-8'

    current_month_col = get_column_name(yyyymm)

    path = os.getcwd()

    #file = "\\betatestMonday 12. March 2018.csv"

    df = pd.read_csv(path + file, encoding='CP949')

    market_median = df[current_month_col].median()

    if code == 'ALL':
        stock_df = df
        average_beta  = 9999999999;
    else:
        stock_df = df[df['code'] == int(code)]
        average_beta = average_prev6_beta(start_month, stock_df)
        print(average_beta)

    return current_month_col, average_beta, market_median, stock_df
    # 투자 당월 column name, 직전 6 개월 평균 beta, market_median, market 전체 dataframe

if __name__ == '__main__':
    #---- market 전체(혹은 fscor >= 7 등 selectively) 종목의 monthly beta 를 구하고 그 file 에서 특정 종목의
    #---- 직전 6 개월 평균 beta 와 당월의 market median beta 비교하여
    #---- (직전6개월 평균 beta) > (당월 median beta) : short
    #---- (직전6개월 평균 beta) < (당월 median beta) : long
    #code = 'ALL' # 전종목 일괄처리 : 'ALL'
    code = 'ALL' # 전종목 일괄처리 : 'ALL'
    yyyymm = '2016-12'  # 투자하려는 당월
    start_month = '2016-6'  # 평균계산 시작월
    file = "\\betatestThursday 15. March 2018.csv"
    current_month_col, average_beta, market_median, df = get_median(code, yyyymm, start_month, file)
    print(current_month_col)
    print(average_beta)
    print(market_median)
    print()
    print(df)
