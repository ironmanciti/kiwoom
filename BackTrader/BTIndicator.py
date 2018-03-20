import datetime
import backtrader as bt
from extensions.indicators import SwingInd

import sys
import pandas as pd
sys.path.append('../lib/')
from dbConnect import *

class SimpleStrategy(bt.Strategy):

    def __init__(self):
        self.piv = SwingInd(period=7)

#---------------------------------------------------------------------
if __name__ == "__main__":

    cerebro = bt.Cerebro()

    cerebro.addstrategy(SimpleStrategy)

    code = '005930'
    fromdate = datetime.datetime(2010,1,1)
    todate   = datetime.datetime(2017,1,1)
    db_frame = pd.read_sql("SELECT * from dailycandle where code = {} and date between '{}' \
                            and '{}'".format(code, fromdate, todate), con=engine, index_col=["date"])
    db_frame['openinterest'] = 0
    db_frame.drop(['code'], axis=1,inplace=True);
    data = bt.feeds.PandasData(dataname=db_frame)
    #------------------------------------------------------------------
    cerebro.adddata(data)

    cerebro.run()
    #----------------- Plot result -------------------------------------
    cerebro.plot(style='candlestick')
