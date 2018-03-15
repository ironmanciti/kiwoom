#!/usr/bin/python

# -*- coding: 949 -*-

import pandas as pd
import os
from codesAndItems import *

# Processing option
market_group = "유가증권시장상장법인"  # or '코스닥시장상장법인'

output_single = "F_SCORE_single_fs_2016_4Q"

file_list_current_single = \
                   ["\\2016_4Q_FS\\_2016_사업보고서_01_재무상태표_20170524.csv",
                    "\\2016_4Q_FS\\_2016_사업보고서_02_손익계산서_20170524.csv",
                    "\\2016_4Q_FS\\_2016_사업보고서_03_포괄손익계산서_20170524.csv",
                    "\\2016_4Q_FS\\_2016_사업보고서_04_현금흐름표_20170524.csv"]

file_list_previous_single = \
                   ["\\2015_4Q_FS\\_2015_사업보고서_01_재무상태표_20160531.csv",
                    "\\2015_4Q_FS\\_2015_사업보고서_02_손익계산서_20160531.csv",
                    "\\2015_4Q_FS\\_2015_사업보고서_03_포괄손익계산서_20160531.csv",
                    "\\2015_4Q_FS\\_2015_사업보고서_04_현금흐름표_20160601.csv"]

output_consolidated = "F_SCORE_consolidated_fs_2016_4Q"

file_list_current_consolidated  = \
                   ["\\2016_4Q_FS\\_2016_사업보고서_01_재무상태표_연결_20170524.csv",
                    "\\2016_4Q_FS\\_2016_사업보고서_02_손익계산서_연결_20170524.csv",
                    "\\2016_4Q_FS\\_2016_사업보고서_03_포괄손익계산서_연결_20170524.csv",
                    "\\2016_4Q_FS\\_2016_사업보고서_04_현금흐름표_연결_20170524.csv"]

file_list_previous_consolidated = \
                    ["\\2015_4Q_FS\\_2015_사업보고서_01_재무상태표_연결_20160531.csv",
                     "\\2015_4Q_FS\\_2015_사업보고서_02_손익계산서_연결_20160531.csv",
                     "\\2015_4Q_FS\\_2015_사업보고서_03_포괄손익계산서_연결_20160531.csv",
                     "\\2015_4Q_FS\\_2015_사업보고서_04_현금흐름표_연결_20160601.csv"]
#-----------------------------------------------------------------------------------------------------
def print_values(**kwargs):
    print("\n".join("{}\t{}".format(k, v) for k, v in kwargs.items()))

def file_pre_process(file):
    path = os.getcwd();

    df = pd.read_csv(path + file)

    df = df.loc[:,['시장구분','종목코드', '회사명', '결산기준일', '항목코드', '항목명', '당기', '전기', '전전기']]
    df.columns = ['market_group','company', 'company_name', 'closing', 'item', 'item_name', 'current',
                      'previous', 'ex_previous']

    df['market_group'] = df['market_group'].str.strip()
    df['company'] = df['company'].str.strip()
    df['company_name'] = df['company_name'].str.strip()
    df['item'] = df['item'].str.strip()
    df['item_name'] = df['item_name'].str.strip()

    return df

def f_score(file_list_current, file_list_previous, output_name):
    fs_cur = pd.DataFrame()
    fs_prev = pd.DataFrame()

    for file_cur, file_prev in zip(file_list_current, file_list_previous):

        fs = file_pre_process(file_cur)
        fs_cur = fs_cur.append(fs, ignore_index=True)

        fs = file_pre_process(file_prev)
        fs_prev = fs_prev.append(fs, ignore_index=True)

    fs_cur  = fs_cur[fs_cur['market_group'] == market_group]  # Select Market Group
    fs_prev = fs_prev[fs_prev['market_group'] == market_group]  # 유가증권시장 or 코스닥시장법인

    fs_cur  =  fs_cur[(fs_cur['item'].isin(processing_items)  | fs_cur['item_name'].isin(processing_items))]
    fs_prev = fs_prev[(fs_prev['item'].isin(processing_items) | fs_prev['item_name'].isin(processing_items))]

    fs_prev_codes = fs_prev['company'] # 전년도 자료가 있는 경우만 F-SCORE 계산
    fs_cur = fs_cur[fs_cur['company'].isin(list(fs_prev_codes))]

    #### test 용 두개 회사만 sample 처리
    #fs_prev = fs_prev[fs_prev['company'].isin(['[020560]','[005930]','[002390]','[053690]','[020000]'])]
    #fs_cur = fs_cur[fs_cur['company'].isin(['[020560]','[005930]','[002390]','[053690]','[020000]'])]

    company_list = pd.unique(fs_cur[['company','company_name']].values)

    #company_list = [('[020560]', '아시아나항공'),('[005930]', '삼성전자')]

    f_scores = {}
    for company, name in company_list:
        f_score = 0
        skip = False

        Net_Income_prev = fs_prev[(fs_prev['company'] == company) &
                (fs_prev['item'].isin(net_income_codes) | fs_prev['item_name'].isin(net_income_items))]['current']
        if Net_Income_prev.values.size == 0:
            skip = True
            print('Net Income Previous Year not found')

        Net_Income = fs_cur[(fs_cur['company'] == company) &
                (fs_cur['item'].isin(net_income_codes) | fs_cur['item_name'].isin(net_income_items))]['current']
        if Net_Income.values.size == 0:
            skip = True
            print('Net Income not found')

        Total_Asset_prev  = fs_prev[(fs_prev['company'] == company) &
                (fs_prev['item'].isin(asset_codes) | fs_prev['item_name'].isin(asset_items))]['previous']
        if Total_Asset_prev.values.size == 0:
            skip = True
            print('Total Asset Previous Year not found')

        Total_Asset  = fs_cur[(fs_cur['company'] == company) &
                (fs_cur['item'].isin(asset_codes) | fs_cur['item_name'].isin(asset_items))]['previous']
        if Total_Asset.values.size == 0:
            skip = True
            print('Total Asset not found')

        Avg_Total_Asset_prev_1  = fs_prev[(fs_prev['company'] == company) &
                (fs_prev['item'].isin(asset_codes) | fs_prev['item_name'].isin(asset_items))]['previous']
        Avg_Total_Asset_prev_2  = fs_prev[(fs_prev['company'] == company) &
                (fs_prev['item'].isin(asset_codes) | fs_prev['item_name'].isin(asset_items))]['current']

        Avg_Total_Asset_prev = (Avg_Total_Asset_prev_1 + Avg_Total_Asset_prev_2) / 2
        if Avg_Total_Asset_prev.values.size == 0:
            skip = True
            print('Average Total Asset previous year not found')

        Avg_Total_Asset_1  = fs_cur[(fs_cur['company'] == company) &
                (fs_cur['item'].isin(asset_codes) | fs_cur['item_name'].isin(asset_items))]['previous']
        Avg_Total_Asset_2  = fs_cur[(fs_cur['company'] == company) &
                (fs_cur['item'].isin(asset_codes) | fs_cur['item_name'].isin(asset_items))]['current']

        Avg_Total_Asset = (Avg_Total_Asset_1 + Avg_Total_Asset_2) / 2
        if Avg_Total_Asset.values.size == 0:
            skip = True
            print('Average Total Asset not found')

        Cash_Flow =  fs_cur[(fs_cur['company'] == company) &
                (fs_cur['item'].isin(cash_flow_codes) | fs_cur['item_name'].isin(cash_flow_items) )]['current']
        if Cash_Flow.size == 0:
            skip = True
            print('Cash Flow not found')

        Long_Liability_prev =  fs_prev[(fs_prev['company'] == company) &
                (fs_prev['item'].isin(long_liability_codes) | fs_prev['item_name'].isin(long_liability_items))]['current']
        if Long_Liability_prev.size == 0:
            skip = True
            print('Long Liability Previous Year not found')

        Long_Liability =  fs_cur[(fs_cur['company'] == company) &
                (fs_cur['item'].isin(long_liability_codes) | fs_cur['item_name'].isin(long_liability_items))]['current']
        if Long_Liability.size == 0:
            skip = True
            print('Long Liability not found')

        Current_Liability_prev =  fs_prev[(fs_prev['company'] == company) &
                (fs_prev['item'].isin(current_liability_codes) | fs_prev['item_name'].isin(current_liability_items))]['current']
        if Current_Liability_prev.size == 0:
            skip = True
            print('Current Liability previous year not found')

        Current_Liability =  fs_cur[(fs_cur['company'] == company) &
                (fs_cur['item'].isin(current_liability_codes) | fs_cur['item_name'].isin(current_liability_items))]['current']
        if Current_Liability.size == 0:
            skip = True
            print('Current Liability not found')

        Current_Asset_prev =  fs_prev[(fs_prev['company'] == company) &
                (fs_prev['item'].isin(current_asset_codes) | fs_prev['item_name'].isin(current_asset_items))]['current']
        if Current_Asset_prev.size == 0:
            skip = True
            print('Current Asset previous year not found')

        Current_Asset =  fs_cur[(fs_cur['company'] == company) &
                (fs_cur['item'].isin(current_asset_codes) | fs_cur['item_name'].isin(current_asset_items))]['current']
        if Current_Asset.size == 0:
            skip = True
            print('Current Asset not found')

        EQ_prev =  fs_prev[(fs_prev['company'] == company) &
                (fs_prev['item'].isin(capital_codes) | fs_prev['item_name'].isin(capital_items))]['current']
        if EQ_prev.size == 0:
            skip = True
            print('EQuity previou year not found')

        EQ =  fs_cur[(fs_cur['company'] == company) &
                  (fs_cur['item'].isin(capital_codes) | fs_cur['item_name'].isin(capital_items))]['current']
        if EQ.size == 0:
            skip = True
            print('EQuity not found')

        Total_Sales_prev =  fs_prev[(fs_prev['company'] == company) &
                (fs_prev['item'].isin(total_sales_codes) | fs_prev['item_name'].isin(total_sales_items))]['current']
        if Total_Sales_prev.size == 0:
            skip = True
            print('Total Sales previous year not found')

        Total_Sales =  fs_cur[(fs_cur['company'] == company) &
                (fs_cur['item'].isin(total_sales_codes) | fs_cur['item_name'].isin(total_sales_items))]['current']
        if Total_Sales.size == 0:
            skip = True
            print('Total Sales not found')

        G_Margin_prev =  fs_prev[(fs_prev['company'] == company) &
                (fs_prev['item'].isin(g_margin_codes) | fs_prev['item_name'].isin(g_margin_items))]['current']
        if G_Margin_prev.size == 0:
            skip = True
            print('Gross Margin previous year not found')

        G_Margin =  fs_cur[(fs_cur['company'] == company) &
                (fs_cur['item'].isin(g_margin_codes) | fs_cur['item_name'].isin(g_margin_items))]['current']
        if G_Margin.size == 0:
            skip = True
            print('Gross Margin not found')

        if skip:
            print(company, name, 'skipped ......')
        else:
            #** ROA
            ROA = Net_Income.values[0] / Total_Asset.values[0]
            if ROA > 0:
                f_score += 1
            #** CFO
            CFO = Cash_Flow.values[0] / Total_Asset.values[0]
            if CFO > 0:
                f_score += 1
            #** Delta ROA
            ROA_prev = Net_Income_prev.values[0] / Total_Asset_prev.values[0]
            if ROA - ROA_prev > 0:
                f_score += 1
            #** Accrual
            if CFO > ROA :
                f_score += 1
            #** Delta Leverage
            LEV = Long_Liability.values[0] / Avg_Total_Asset.values[0]
            LEV_prev = Long_Liability_prev.values[0] / Avg_Total_Asset_prev.values[0]
            if (LEV - LEV_prev) < 0:
                f_score += 1
            #** Delta Liquitity
            LEQ = Current_Asset.values[0] / Current_Liability.values[0]
            LEQ_prev = Current_Asset_prev.values[0] / Current_Liability_prev.values[0]
            if (LEQ - LEQ_prev) > 0:
                f_score += 1
            #** EQ_OFFER
            if EQ_prev.values[0] == EQ.values[0]:
                f_score += 1
            #** Delta margin
            GMO = G_Margin.values[0] / Total_Sales.values[0]
            GMO_prev = G_Margin_prev.values[0] / Total_Sales_prev.values[0]
            if (GMO - GMO_prev) > 0:
                f_score += 1
            #** Delta Turnover
            ATR = Total_Sales.values[0] / Total_Asset.values[0]
            ATR_prev = Total_Sales_prev.values[0] /  Total_Asset_prev.values[0]
            if (ATR - ATR_prev) > 0:
                f_score += 1

            f_scores[company+ ' ' + name] = {
                        'ROA': ROA,
                        'ROA_prev': ROA_prev,
                        'CFO': CFO,
                        'LEV': LEV,
                        'LEV_prev': LEV_prev,
                        'LEQ': LEQ,
                        'LEQ_prev': LEQ_prev,
                        'GMO': GMO,
                        'GMO_prev': GMO_prev,
                        'ATR': ATR,
                        'ATR_prev': ATR_prev,
                        'fscore': f_score,
                        }

            # if company == '[005930]':
            #     print_values(company=company,
            #             name=name,
            #             Net_Income_prev = Net_Income_prev.values[0],
            #             Net_Incom       = Net_Income.values[0],
            #             Total_Asset_prev = Total_Asset_prev.values[0],
            #             Total_Asset      = Total_Asset.values[0],
            #             Avg_Total_Asset_prev = Avg_Total_Asset_prev.values[0],
            #             Avg_Total_Asset      = Avg_Total_Asset.values[0],
            #             Long_Liability_prev = Long_Liability_prev.values[0],
            #             Long_Liability      = Long_Liability.values[0],
            #             Current_Asset_prev = Current_Asset_prev.values[0],
            #             Current_Asset      = Current_Asset.values[0],
            #             Current_Liability_prev = Current_Liability_prev.values[0],
            #             Current_Liability      = Current_Liability.values[0],
            #             EQ_prev = EQ_prev.values[0],
            #             EQ      = EQ.values[0],
            #             G_Margin_prev = G_Margin_prev.values[0],
            #             G_Margin      = G_Margin.values[0],
            #             Total_Sales_prev = Total_Sales_prev.values[0],
            #             Total_Sales      = Total_Sales.values[0],
            #             Cash_Flow = Cash_Flow.values[0]
            #             )

    items_list = []
    items_label = ['Code', 'Name', 'fscore', 'ROA', 'ROA_prev', 'CFO', 'LEV', 'LEV_prev', 'LEQ', 'LEQ_prev',\
                   'GMO', 'GMO_prev','ATR', 'ATR_prev']

    for key, val in f_scores.items():
        if len(val) > 0:
            code = key.replace('[','').replace(']','').split()
            code[0] = 'A' + code[0]
            items_tuple = (code[0],code[1],val['fscore'],val['ROA'],val['ROA_prev'],val['CFO'],val['LEV'],\
                val['LEV_prev'],val['LEQ'],val['LEQ_prev'],val['GMO'],val['GMO_prev'],val['ATR'],val['ATR_prev'])
            items_list.append(items_tuple)

    df = pd.DataFrame.from_records(items_list, columns=items_label)

    df.to_csv(output_name + '.csv')

if __name__ == '__main__':
    f_score(file_list_current_single, file_list_previous_single, output_single)
    f_score(file_list_current_consolidated, file_list_previous_consolidated, output_consolidated)
