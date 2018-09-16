import datetime
import backtrader as bt
import math

import pandas as pd
import random

import sys
sys.path.append('../lib/')
from dbConnect import *

stock = '003620'
alt1 = (stock,datetime.datetime(2017,1,1),datetime.datetime(2017,4,1))
alt2 = (stock,datetime.datetime(2017,1,1),datetime.datetime(2017,7,1))
alt3 = (stock,datetime.datetime(2017,1,1),datetime.datetime(2017,10,1))
alt4 = (stock,datetime.datetime(2017,1,1),datetime.datetime(2018,1,1))

class maxRiskSizer(bt.Sizer):
    '''
    Returns the number of shares rounded down that can be purchased for the
    max rish tolerance
    '''
    params = (('risk', 0.03),)

    def __init__(self):
        if self.p.risk > 1 or self.p.risk < 0:
            raise ValueError('The risk parameter is a percentage which must be'
                'entered as a float. e.g. 0.5')

    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy == True:
            size = math.floor((cash * self.p.risk) / data[0])
        else:
            size = math.floor((cash * self.p.risk) / data[0]) * -1
        return size

class TestStrategy(bt.Strategy):
    params = (
        ('maperiod', 15),
        ('printlog', False),
    )

    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close   # datas[0] dataseries 의 close line 참조
        self.order = None
        self.buyprice = None
        self.buycomm = None
        
        self.log('d, {}'.format(self.getdatanames()),doprint=True)

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
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS {:.2f}, NET {:.2f}'.format(trade.pnl, trade.pnlcomm),doprint=True)

    def start(self):
        self.log('Starting Value {0:,}'
                    .format(round(self.broker.getvalue())),doprint=True)

    def next(self):
        #self.log('Close, {0:,}'.format(round(self.dataclose[0])),doprint=True)
        highs = self.data.high.get()
        print(self.datas[1]._name,'highest', max(highs))
        print(self.data._name)
        self.log('High, {0:,}'.format(round(self.data.high.get()[0])),doprint=True)
        self.log('Close, {0:,}'.format(round(self.datas[0].close[0])),doprint=True)
        #self.log('volume1, {0:,}'.format(round(self.datas[1].volume[0])),doprint=True)
        #self.log('lenght of the line, {}'.format(len(self.datas[1])),doprint=True)
        #self.log('lenght of current bar, {}'.format(len(self)),doprint=True)
        #for d in self.getdatanames():
            #DATA = self.getdatabyname(d)
            #self.log('posiion = , {}'.format(DATA),doprint=True)

        #for i, d in enumerate(self.datas):
            #dt, dn = self.datetime.date(), d._name
            #pos = self.getposition(d).size
            #pos2 = self.getpositionbyname(dn).size
            #self.log('pos, {0:,}'.format(round(pos)),doprint=True)
            #self.log('pos2, {0:,}'.format(round(pos2)),doprint=True)
            #self.close(d)

        if self.order:
            return

        if not self.position:
            self.log('BUY CREATED, {0:,}'.format(round(self.dataclose[0])),doprint=True)
            self.order = self.buy()

    def stop(self):
        self.log('Ending Value {0:,}'
                    .format(round(self.broker.getvalue())),doprint=True)

#---------------------------------------------------------------------
def main(icode, ifromdate, itodate):

    startcash = 100000000

    cerebro = bt.Cerebro()

    #------------- add or opt strategy --------------------------
    cerebro.addstrategy(TestStrategy)
    # strats = cerebro.optstrategy(
    #     TestStrategy,
    #     maperiod=range(30,360)
    # )
    #-------------------  direct read from stockdb ----------------------
    code = icode
    fromdate = ifromdate
    todate   = itodate
    #print("\n")
    #print("code= {}, fromdate= {}, todate= {}".format(code, fromdate.date().isoformat(), todate.date().isoformat()))
    db_frame = pd.read_sql("SELECT * from dailycandle where code = {} and date between '{}' \
                            and '{}'".format(code, fromdate, todate), con=engine, index_col=["date"])
    #db_frame['adjclose'] = 99

    db_frame.drop(['code'], axis=1,inplace=True);
    data = bt.feeds.PandasData(dataname=db_frame, name='aaa')
    #------------------------------------------------------------------
    cerebro.adddata(data)

    code = "000050"
    fromdate = ifromdate
    todate   = itodate
    #print("\n")
    #print("code= {}, fromdate= {}, todate= {}".format(code, fromdate.date().isoformat(), todate.date().isoformat()))
    db_frame = pd.read_sql("SELECT * from dailycandle where code = {} and date between '{}' \
                            and '{}'".format(code, fromdate, todate), con=engine, index_col=["date"])
    db_frame.drop(['code'], axis=1,inplace=True);
    data = bt.feeds.PandasData(dataname=db_frame, name='000050')
    #------------------------------------------------------------------
    cerebro.adddata(data)

    cerebro.broker.setcash(startcash)
    #------------------ Add stake size & commission -----------------------
    # cerebro.addsizer(bt.sizers.FixedSize, stake=100)
    cerebro.addsizer(maxRiskSizer, risk=0.99)
    cerebro.broker.setcommission(commission=0.00165)           # broker commission
    #----------------- Optimize Strategy --------------------------------------
    cerebro.run()

    portvalue = cerebro.broker.getvalue()
    pnl = round(portvalue - startcash)

    days = (todate - fromdate).days
    rate = pnl / startcash * 365 / days  * 100

    #Print out the final Result
    print('P/L: KRW {0:,}  Annualized Rate: {1:.2f} %'.format(pnl, rate))
    #----------------- Plot result -------------------------------------
    cerebro.plot(style='candlestick')

if __name__ == '__main__':
    for icode, ifromdate, itodate in [alt1, alt2, alt3, alt4]:
        main(icode, ifromdate, itodate)
