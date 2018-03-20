import datetime
import backtrader as bt

import sys
import pandas as pd
sys.path.append('../lib/')
from dbConnect import *

class fistStrategy(bt.Strategy):

    params = (
        ('period', 21),
    )

    def __init__(self):
        self.startcash = self.broker.getvalue()
        self.rsi = bt.indicators.RSI_SMA(self.data.close,period=self.params.period)

    def next(self):
        if not self.position:
            if self.rsi < 30:
                self.order = self.buy(size=100)
        else:
            if self.rsi > 70:
                self.order = self.sell(size=100)

if __name__ == "__main__":
    startcash = 100000000

    cerebro = bt.Cerebro(optreturn=False)

    cerebro.optstrategy(fistStrategy, period=range(14,21))

    #-------------------  direct read from stockdb ----------------------
    code = '005930'
    fromdate = datetime.datetime(2010,1,1)
    todate   = datetime.datetime(2017,1,1)
    db_frame = pd.read_sql("SELECT * from dailycandle where code = {} and date between '{}' \
                            and '{}'".format(code, fromdate, todate), con=engine, index_col=["date"])
    db_frame['openinterest'] = 0
    db_frame.drop(['code'], axis=1,inplace=True);
    data = bt.feeds.PandasData(dataname=db_frame)

    cerebro.adddata(data)

    cerebro.broker.setcash(startcash)              # start cash

    opt_runs = cerebro.run()

    #Generate restults list
    final_results_list = []
    for run in opt_runs:
        for strategy in run:
            value = round(strategy.broker.get_value(),2)
            PnL = round(value - startcash, 2)
            period = strategy.params.period
            final_results_list.append([period, PnL])
    # Sort Results list
    by_period = sorted(final_results_list, key=lambda x: x[0])
    by_PnL = sorted(final_results_list, key=lambda x: x[1], reverse=True)

    #Print out the final Result
    print('Results: Ordered by period:')
    for result in by_period:
        print('Period: {}, PnL: {}'.format(result[0], result[1]))
    print('Results: Ordered by Profit:')
    for result in by_PnL:
        print('Period: {}, PnL: {}'.format(result[0], result[1]))

    cerebro.plot(style='candlestick')
