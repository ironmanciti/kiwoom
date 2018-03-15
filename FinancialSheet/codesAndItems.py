# BS items
asset_codes = ['ifrs_Assets']
asset_items = ['자산총계','자산 총계']
current_asset_codes = ['ifrs_CurrentAssets']
current_asset_items = ['유동자산','유동 자산']
capital_codes = ['dart_ContributedEquity']
capital_items = ['자본금','1.자본금','보통주자본금','자 본 금','I.자본금','I. 자본금','자본',\
                '1. 납입자본금','납입자본','Ⅰ. 자본금','Ⅰ.자본금','자본금.','1)자본금']
long_liability_codes = ['ifrs_NoncurrentLiabilities']
long_liability_items = ['장기차입금','비유동부채','비유동 부채']
current_liability_codes = ['ifrs_CurrentLiabilities']
current_liability_items = ['유동부채','유동 부채']
short_term_loans_codes = ['dart_ShortTermBorrowings','ifrs_OtherCurrentFinancialLiabilities',
                          'ifrs_CurrentPortionOfLongtermBorrowings']
short_term_loans_items = ['단기차입금','단기금융부채','유동차입금','단기차입금','단기차입부채']
income_taxes_payable_codes = ['ifrs_CurrentTaxLiabilities','dart_PaymentsOfIncomeTaxesPayable','ifrs_CurrentTaxAssets']
income_taxes_payable_items = [' 3. 당기법인세부채','당기법인세부채','법인세부채']

# PL items
net_income_items = ['당기순이익(손실)','V. 당기순이익','Ⅹ.당기순이익(손실)','V. 당기순이익(손실)',\
                   'VI. 당기순이익(손실)','당기순이익','연결당기순이익','Ⅹ.당기순이익','당기 순이익']
net_income_codes = ['ifrs_ProfitLoss']

income_taxes_codes = ['ifrs_IncomeTaxExpenseContinuingOperations']
income_taxes_items = ['법인세비용','계속영업법인세비용']
total_sales_items = ['매출','영업수익','매출액','Ⅰ.매 출 액','수익','영업 수익','영업 이익(손실)']
total_sales_codes = ['ifrs_Revenue']
g_margin_codes = ['dart_OperatingIncomeLoss','ifrs_GrossProfit']
g_margin_items = ['매출총이익','영업이익','매출 총이익','Ⅲ. 매출총이익','Ⅲ. 매출총이익',\
                  '영업이익(손실)','Ⅲ.매출 총이익','영업 이익(손실)','III. 영업이익(손실)']

# CASHFLOW items
cash_flow_codes = ['ifrs_CashFlowsFromUsedInOperatingActivities']
cash_flow_items = ['Ⅰ.영업활동으로 인한 현금흐름','영업활동 현금흐름','영업활동현금흐름','영업활동으로 인한 현금흐름',\
                    '영업활동순현금흐름','Ⅰ.영업활동으로 인한 현금흐름','영업활동으로 인한 현금 흐름',\
                    'Ⅰ.영업활동으로인한 현금흐름','영업활동으로인한순현금흐름']

bs_items = asset_codes + asset_items + long_liability_codes + long_liability_items + \
            current_liability_codes + current_liability_items + short_term_loans_codes + short_term_loans_items + \
            income_taxes_payable_codes + income_taxes_payable_items + \
            current_asset_codes + current_asset_items + capital_codes + capital_items

pl_items = net_income_items + net_income_codes + income_taxes_codes + income_taxes_items + \
            total_sales_items + total_sales_codes + g_margin_codes + g_margin_items

cashflow_items = cash_flow_codes + cash_flow_items

processing_items = bs_items + pl_items + cashflow_items
