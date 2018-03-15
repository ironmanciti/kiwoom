#!/usr/bin/python

# -*- coding: 949 -*-

import pandas as pd
import os
from codesAndItems import *

output_single = "accrual_cash_ratio_single_fs_2016_4Q"

file_single_bs =       "\\2016_4Q_FS\\_2016_사업보고서_01_재무상태표_20170524.csv"
file_single_pl =      ["\\2016_4Q_FS\\_2016_사업보고서_02_손익계산서_20170524.csv",
                       "\\2016_4Q_FS\\_2016_사업보고서_03_포괄손익계산서_20170524.csv"]
file_single_cashflow = "\\2016_4Q_FS\\_2016_사업보고서_04_현금흐름표_20170524.csv"

#--------------------------- 연결 재무제표 발표한 회사 -------------
output_consolidated = "accrual_cash_ratio_consolidated_fs_2016_4Q"

file_consolidated_bs =      "\\2016_4Q_FS\\_2016_사업보고서_01_재무상태표_연결_20170524.csv"
file_consolidated_pl =     ["\\2016_4Q_FS\\_2016_사업보고서_02_손익계산서_연결_20170524.csv",
                            "\\2016_4Q_FS\\_2016_사업보고서_03_포괄손익계산서_연결_20170524.csv"]
file_consolidated_cashflow ="\\2016_4Q_FS\\_2016_사업보고서_04_현금흐름표_연결_20170524.csv"
#-----------------------------------------------------------------------------------------------------
def print_values(**kwargs):
    print("\n".join("{}\t{}".format(k, v) for k, v in kwargs.items()))

def file_pre_process(file):
    path = os.getcwd()

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


def filter_items(file, processing_items):
    df = file_pre_process(file)
    df= df[df['market_group'] != '코스닥시장상장법인']  # 코스닥 제외
    df  =  df[(df['item'].isin(processing_items)  | df['item_name'].isin(processing_items))]
    return df

def calc_ratio(file_bs, file_pl, file_cashflow, output_name):
    fs = pd.DataFrame()

    df = filter_items(file_bs, bs_items)
    fs = fs.append(df, ignore_index=True)

    for file in file_pl:
        df = filter_items(file, pl_items)
        fs = fs.append(df, ignore_index=True)

    df = filter_items(file_cashflow, cashflow_items)
    fs = fs.append(df, ignore_index=True)

    company_list = pd.unique(fs[['company','company_name']].values)

    #company_list = [('[020560]', '아시아나항공'),('[005930]', '삼성전자')]

    sloan = {}
    for company, name in company_list:

        skip = False

        asset = fs[(fs['company'] == company) &
                    (fs['item'].isin(asset_codes) | fs['item_name'].isin(asset_items))][['current', 'previous']]

        prev_asset = asset['previous']
        if prev_asset.values.size == 0:
            skip = True
            print('Previous Asset not found')

        current_asset  = asset['current']
        if current_asset.values.size == 0:
            skip = True
            print('Current Asset not found')

        cash_flow =  fs[(fs['company'] == company) &
                (fs['item'].isin(cash_flow_codes) | fs['item_name'].isin(cash_flow_items) )][['current', 'previous']]

        prev_cash_flow = cash_flow['previous']
        if prev_cash_flow.size == 0:
            skip = True
            print('Previous Cash Flow not found')

        current_cash_flow =  cash_flow['current']
        if current_cash_flow.size == 0:
            skip = True
            print('Current Cash Flow not found')

        short_term_loans =  fs[(fs['company'] == company) &
                (fs['item'].isin(short_term_loans_codes) | fs['item_name'].isin(short_term_loans_items))][['current', 'previous']]

        prev_short_term_loans = short_term_loans['previous']
        if prev_short_term_loans.size == 0:
            skip = True
            print('Previous Short Term Loans not found')

        current_short_term_loans = short_term_loans['current']
        if current_short_term_loans.size == 0:
            skip = True
            print('Current Short Term Loans not found' )

        current_liability =  fs[(fs['company'] == company) &
                (fs['item'].isin(current_liability_codes) | fs['item_name'].isin(current_liability_items))][['current', 'previous']]

        prev_current_liability = current_liability['previous']
        if prev_current_liability.size == 0:
            skip = True
            print('Current Liability previous year not found')

        current_current_liability = current_liability['current']
        if current_current_liability.size == 0:
            skip = True
            print('Current Liability not found')

        income_taxes_payable =  fs[(fs['company'] == company) &
                (fs['item'].isin(income_taxes_payable_codes) | fs['item_name'].isin(income_taxes_payable_items))][['current', 'previous']]

        prev_income_taxes_payable =  income_taxes_payable['previous']
        if prev_income_taxes_payable.size == 0:
                skip = True
                print('Previous Income Taxes Payable not found' )

        current_income_taxes_payable =  income_taxes_payable['current']
        if current_income_taxes_payable.size == 0:
                skip = True
                print('Current Income Taxes Payable not found' )

        income_taxes = fs[(fs['company'] == company) &
                (fs['item'].isin(income_taxes_codes) | fs['item_name'].isin(income_taxes_items))]['current']
        if income_taxes.size == 0:
                skip = True
                print('Income Taxes not found' )
                if company == '[006060]':
                    print('income_taxes_codes = ',income_taxes_codes)

        net_income = fs[(fs['company'] == company) &
                (fs['item'].isin(net_income_codes) | fs['item_name'].isin(net_income_items))]['current']
        if net_income.values.size == 0:
            skip = True
            print('Net Income not found')

        # Dep = fs[(fs['company'] == company) & (fs['item'].isin(depreciation_codes))]['current']
        # if Dep.values.size == 0:
        #     skip = True
        #     print('depreciation not found')

        if skip:
            print(company, name, 'skipped ......')
        else:
            Delta_CA = current_asset.values[0] - prev_asset.values[0]

            Delta_Cash = current_cash_flow.values[0] - prev_cash_flow.values[0]

            Delta_CL = current_current_liability.values[0] - prev_current_liability.values[0]

            Delta_STD = current_short_term_loans.values[0] - prev_short_term_loans.values[0]

            Delta_TP = current_income_taxes_payable.values[0] - prev_income_taxes_payable.values[0]

            # Dep = current_cash_flow.values[0] - net_income.values[0] + income_taxes.values[0]
            # Accruals = (Delta_CA - Delta_Cash) - (Delta_CL - Delta_STD - Delta_TP) - Dep

            Accruals = (Delta_CA - Delta_Cash) - (Delta_CL - Delta_STD - Delta_TP)

            average_total_assets = (current_asset.values[0] + prev_asset.values[0]) / 2

            Earnings = net_income.values[0] / average_total_assets

            Accrual_Component = Accruals / average_total_assets

            Cash_Flow_Component = Earnings - Accrual_Component

            sloan[company+ ' ' + name] = []
            sloan[company+ ' ' + name].append(Accrual_Component)
            sloan[company+ ' ' + name].append(Cash_Flow_Component)

            # if company == '[005930]':
            #     print_values(company=company,
            #             name=name,
            #             current_asset =  current_asset.values[0],
            #             prev_asset = prev_asset.values[0],
            #             current_cash_flow = current_cash_flow.values[0],
            #             prev_cash_flow = prev_cash_flow.values[0],
            #
            #             current_current_liability = current_current_liability.values[0],
            #             prev_current_liability = prev_current_liability.values[0],
            #
            #             current_short_term_loans = current_short_term_loans.values[0],
            #             prev_short_term_loans = prev_short_term_loans.values[0],
            #
            #             current_income_taxes_payable = current_income_taxes_payable.values[0],
            #             prev_income_taxes_payable = prev_income_taxes_payable.values[0],
            #
            #             net_income = net_income.values[0],
            #             income_taxes =  income_taxes.values[0]
            #             )

    dict_items = {'Code': [], 'Name': [], 'Accrual Component': [],  'Cash Component': []}

    for key, val in sloan.items():
        code = key.replace('[','').replace(']','').split()
        code[0] = 'A' + code[0]
        dict_items['Code'].append(code[0])
        dict_items['Name'].append(code[1])
        dict_items['Accrual Component'].append(val[0])
        dict_items['Cash Component'].append(val[1])

    df = pd.DataFrame.from_dict(dict_items)

    df.to_csv(output_name + '.csv')

if __name__ == '__main__':
    calc_ratio(file_single_bs, file_single_pl, file_single_cashflow, output_single)
    calc_ratio(file_consolidated_bs, file_consolidated_pl, file_consolidated_cashflow, output_consolidated)
