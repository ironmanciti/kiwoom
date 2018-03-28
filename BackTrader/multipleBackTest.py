import sys
sys.path.append('../lib/')
from dbConnect import *
import pandas as pd
import math
import backtrader as bt
from datetime import datetime

class maCross(bt.Strategy):
    params = (
        ('maperiod', 15),
        ('printlog', False),
    )
    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.inds = dict()
        for i, d in enumerate(self.datas):
            self.inds[d] = dict()

    def next(self):
        for i, d in enumerate(self.datas):
            dt, dn = self.datetime.date(), d._name
            pos = self.getposition(d).size
            if not pos:  # no market / no orders
                max_size = self.broker.getvalue() / d._dataname.close[0]
                self.buy(data=d, size=round(max_size))
            else:
                pass

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:  # broker 에게 order 가 submitted/accepted 상태면 skip
            return

        if order.status in [order.Completed]:                   # order  체결 여부 check
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: {:.2f}, Cost: {:.2f}, Comm: {:.2f}'
                             .format(order.executed.price, order.executed.value, order.executed.comm),doprint=True)
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log('SELL EXECUTED, Price: {:.2f}, Cost: {:.2f}, Comm: {:.2f}'
                             .format(order.executed.price, order.executed.value, order.executed.comm),doprint=True)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        dt = self.data.datetime.date()
        if trade.isclosed:
            print('{} {} Closed: PnL Gross {}, Net {}'.format(
                                                dt,
                                                trade.data._name,
                                                round(trade.pnl,2),
                                                round(trade.pnlcomm,2)))


#Variable for our starting cash
startcash = 100000000

#Create an instance of cerebro
cerebro = bt.Cerebro()

#Add our strategy
cerebro.addstrategy(maCross)

#-------------------  direct read from stockdb ----------------------
code = '000050'
fromdate = datetime(2017,1,1)
todate   = datetime(2017,4,1)
print("\n")
print("code= {}, fromdate= {}, todate= {}".format(code, fromdate.date().isoformat(), todate.date().isoformat()))
db_frame = pd.read_sql("SELECT * from dailycandle where code = {} and date between '{}' \
                        and '{}'".format(code, fromdate, todate), con=engine, index_col=["date"])
db_frame['openinterest'] = 0
db_frame.drop(['code'], axis=1,inplace=True);
data1 = bt.feeds.PandasData(dataname=db_frame)
#-------------------  direct read from stockdb ----------------------
market_code = '001'
fromdate = datetime(2017,1,1)
todate   = datetime(2017,4,1)
KOSPI = pd.read_sql("SELECT * from marketcandle where code= {} and date between '{}' \
                        and '{}'".format(market_code, fromdate, todate), con=engine, index_col=["date"])
KOSPI['openinterest'] = 0
KOSPI.drop(['code'], axis=1,inplace=True);

KOSPI_start_close = KOSPI.ix[0,'close']
KOSPI_end_close   = KOSPI.ix[-1,'close']

data2 = bt.feeds.PandasData(dataname=KOSPI)

#Loop through the list adding to cerebro.
# for i in range(len(datalist)):
cerebro.adddata(data1, name="stock1")
cerebro.adddata(data2, name="stock2")
#------------------------------------------------------
# Set our desired cash start
cerebro.broker.setcash(startcash)

# Run over everything
cerebro.run()

portvalue = cerebro.broker.getvalue()
pnl = math.floor(portvalue - startcash)

days = (todate - fromdate).days
rate = pnl / startcash * 365 / days  * 100

rate_kospi = (KOSPI_end_close - KOSPI_start_close) / KOSPI_start_close * 365 / days * 100

diff = rate - rate_kospi

#Print out the final Result
print('P/L: KRW {0:,}  Annualized Rate: {1:.2f} %'.format(pnl, rate))
print('          KOSPI Annualized Rate: {0:.2f} %'.format(rate_kospi))
print('                     Difference: {0:.2f} %'.format(diff))

#Finally plot the end results
cerebro.plot(style='candlestick')
