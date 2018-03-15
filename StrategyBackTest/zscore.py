from zipline.api import order_target_percent, symbol, record, set_commission, \
                        commission, schedule_function, date_rules, time_rules
from zipline.utils.factory import create_simulation_parameters
from zipline.algorithm import TradingAlgorithm
from datetime import datetime
from pandas import date_range
from zipline.utils.tradingcalendar import trading_day
import pandas as pd
import numpy as np
import sqlite3
import pandas_datareader.data as web

import matplotlib.pyplot as plt
import matplotlib
matplotlib.rc('font',family='Malgun Gothic')

from zipline.api import order_target, record, symbol

code_list = ["KRX:005930", "KRX:005490"]
symbol_list = ['AAPL', 'GOOGL']
start = datetime(2010, 7, 27)
end = datetime(2017, 7, 25)
# zipline 에 등록된 trading day 에 맞는 empty frame 생성
days = date_range(start, end, freq=trading_day)
data = pd.DataFrame(index=days)

for code in code_list:
    data[code] = np.nan
    df = web.DataReader(code, "google", start, end)
    df = df[['Close']]
    df.columns = [code]
    data[code] = df[code]
    data.fillna(method='ffill',inplace=True)

data = data.tz_localize("UTC")
data.columns = [symbol_list]

def initialize(context):
    context.i = 0

    context.SEC   = symbol(symbol_list[0])
    context.POSCO = symbol(symbol_list[1])

    context.long_on_spread = False
    context.shorting_spread = False

    set_commission(commission.PerDollar(cost=0.00165)) # 0.165% commission


def handle_data(context, data):
    context.i += 1
    if context.i < 30:
        return
    
    SEC = context.SEC
    POSCO = context.POSCO

    prices = data.history([SEC, POSCO], 'price', 30, '1d')
    
    short_prices = prices.iloc[-1:] # 30일 단위로 받은 price 의 마지막날 가격
    # spread
    mavg_30 = np.mean(prices[SEC] - prices[POSCO]) # 삼성전자와 POSCO 30 일 가격 차이의 이동평균
    std_30 = np.std(prices[SEC] - prices[POSCO])   # 삼성전자와 POSCO 의 30일 STD

    mavg_1 = np.mean(short_prices[SEC] - short_prices[POSCO])  # 삼성전자와  POSCO의 가격차이

    if std_30 > 0:
        zscore = (mavg_1 - mavg_30) / std_30

        if zscore > 1.0 and not context.shorting_spread:
            order_target_percent(SEC, -0.5)
            order_target_percent(POSCO, 0.5)
            context.shorting_spread = True
            context.long_on_spread = False
        elif zscore < 1.0 and not context.long_on_spread:
            order_target_percent(SEC, -0.5)
            order_target_percent(POSCO, 0.5)
            context.shorting_spread = False
            context.long_on_spread = True
        elif abs(zscore) < 0.1:
            order_target_percent(SEC, 0)
            order_target_percent(POSCO, 0)
            context.shorting_spread = False
            context.long_on_spread = False

        record(zscore=zscore)

algo = TradingAlgorithm(sim_params=create_simulation_parameters(\
    capital_base=100000000), initialize=initialize, handle_data=handle_data)
perf = algo.run(data)

# 종목 한글명

plt.plot(perf.portfolio_value)
plt.show()
