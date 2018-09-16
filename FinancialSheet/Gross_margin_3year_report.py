# -*- coding: utf-8 -*-
"""
3 년간 계속 영업이익 흑자인 회사 중 52주 주가수준이 최저가에서 20% 이내에 있는 회사
코스피, 코스닥 구분
"""
import sys
sys.path.append('../lib/')
from dbConnect import *
from kiwoomMain import *
import sqlalchemy
import pandas as pd
import numpy as np

period_years = set(['2015', '2016', '2017'])

sql = "select * from financesheet where item_code='dart_OperatingIncomeLoss'"
df_all = pd.read_sql(sql, con=engine)

df_all['year'] = df_all['closing_date'].str[:4]

loss_codes = df_all[df_all['amount'] < 0].code.tolist()

df_all = df_all[~df_all['code'].isin(loss_codes)]

df_all.drop(columns=['item_name', 'closing_date'],inplace=True)

df2015 = df_all.loc[df_all.year == '2015', :]
df2016 = df_all.loc[df_all.year == '2016', :]
df2017 = df_all.loc[df_all.year == '2017', :]

df_all = pd.merge(df2015, df2016, on=['kind','smarket','code','code_name','item_code'])
df_all = pd.merge(df_all, df2017,on=['kind','smarket','code','code_name','item_code'])

df_all['highest_250'] = np.nan
df_all['lowest_250']  = np.nan
df_all['current_price'] = np.nan

profit_codes = df_all.code

app = QApplication(sys.argv)
kiwoom = Kiwoom()
kiwoom.comm_connect()

def price(code):
    kiwoom.set_input_value("종목코드", code)
    kiwoom.comm_rq_data("opt10001_req", "opt10001", 0, "2000")
    highest_250 = kiwoom.highest_250
    lowest_250 = kiwoom.lowest_250
    current_price = kiwoom.current_price
    
    return (highest_250, lowest_250, current_price)
    
for k, code in profit_codes[:50].items():
    time.sleep(TR_REQ_TIME_INTERVAL)
    highest_250, lowest_250, current_price = price(code)
    
    if current_price <= (-1 * lowest_250 * 1.2):
        
        df_all.loc[k, 'highest_250'] = highest_250
        df_all.loc[k, 'lowest_250'] = lowest_250
        df_all.loc[k, 'current_price'] = current_price
        
        print(code)
        print(highest_250)
        print(lowest_250 * -1)
        print(current_price)
        print()

print("complete")

