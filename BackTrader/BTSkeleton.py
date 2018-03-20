#"2017-04-01"   # 투자 시작월

# 1   000120  CJ대한통운  0.496539  0.514243
# 40  014680   한솔케미칼  0.494133  0.514243
# 8   002240    고려제강  0.491457  0.514243
# 38  012630    현대산업  0.466800  0.514243
# 0   000050      경방  0.440761  0.514243
#
# Short Strategy : top 5 of 6mAVG > Median
#       code    name     6mAVG    Median
# 58  069260     휴켐스  0.531404  0.514243
# 15  003550      LG  0.542610  0.514243
# 23  005850     에스엘  0.545041  0.514243
# 61  097950  CJ제일제당  0.554584  0.514243
# 17  004170     신세계  0.600035  0.514243

import datetime
import backtrader as bt
import backtrader.indicators as btind
import argparse

import pandas as pd
from pandas import Series, DataFrame
import random
from copy import deepcopy
from extensions.indicators import SwingInd

import sys
sys.path.append('../lib/')
from dbConnect import *

class exampleSizer(bt.Sizer):
    params = (('size', 1),)
    # called everytime strategy makes self.buy() or self.sell()
    # comminfo - broker commission data
    # cash - cash available in the account
    # data - access to the data
    # isbuy - whether the order is buy or sell (True: buy, False: sell)
    def _getsizing(self, comminfo, cash, data, isbuy):
        return self.p.size


class printSizingParams(bt.Sizer):
    '''
    Prints the sizing parameters and values returned from class methods.
    '''
    def _getsizing(self, comminfo, cash, data, isbuy):
        #Strategy Method example
        pos = self.strategy.getposition(data)
        #Broker Methods example
        acc_value = self.broker.getvalue()

        #Print results
        print('----------- SIZING INFO START -----------')
        print('--- Strategy method example')
        print(pos)
        print('--- Broker method example')
        print('Account Value: {}'.format(acc_value))
        print('--- Param Values')
        print('Cash: {}'.format(cash))
        print('isbuy??: {}'.format(isbuy))
        print('data[0]: {}'.format(data[0]))
        print('------------ SIZING INFO END------------')

        return 0

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

        # pending order 유무 및 buyprice/commission 추적
        self.order = None           # pending 되어 있는 order 가 없음
        self.buyprice = None
        self.buycomm = None
        self.startcash = self.broker.getvalue()  #Returns the portfolio value of the given datas (if datas is None, then the total portfolio value will be returned

        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod)

        self.rsi = bt.indicators.RSI_SMA(self.data.close,period=self.params.period)

        # indicators for the plotting show
        # bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
#         bt.indicators.WeightedMovingAverage(self.datas[0], period=25, subplot=True)
#         bt.indicators.StochasticSlow(self.datas[0])
#         bt.indicators.MACDHisto(self.datas[0])
#         rsi = bt.indicators.RSI(self.datas[0])
#         bt.indicators.SmoothedMovingAverage(rsi, period=10)
#         bt.indicators.ATR(self.datas[0], plot=False)
#         bt.indicators.RSI_SMA(self.datas[0], period=21)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:  # broker 에게 order 가 submitted/accepted 상태면 skip
            return

        if order.status in [order.Completed]:                   # order  체결 여부 check
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: {:.2f}, Cost: {:.2f}, Comm: {:.2f}'
                             .format(order.executed.price, order.executed.value, order.executed.comm))
            elif order.issell():
                self.log('SELL EXECUTED, Price: {:.2f}, Cost: {:.2f}, Comm: {:.2f}'
                             .format(order.executed.price, order.executed.value, order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        if not order.alive():
            self.order = None                    # pending 되어 있는 order 가 없음 표시

        self.order = None

    def notify_trade(self, trade):
        if trade.justopned:
            print('----TRADE OPENED ------')
            print('Size: {}'.format(trade.size))
        elif trade.isclosed:
            print('----TRADE CLOSED ------')
            print('Profit, Gross {}, Net {}'.format(
                                            round(trade.pnl,2),
                                            round(trade.pnlcomm,2)))
        else:
            return

        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS {:.2f}, NET {:.2f}'.format(trade.pnl, trade.pnlcomm))

    def start(self):
        self.order = None           # sentinel to avoid operations to pending order

    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])

        if self.order:       # keep track of the created order to avoid a 2nd order
            return

        if not self.position:
            if self.dataclose[0] > self.sma[0]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()
        else:
            if self.dataclose[0] < self.sma[0]:      # buy 조건이 아니면 exibars 길이만큼 가지고 있다 sell
                self.log('SELL CREATED, {:.2f}'.format(self.dataclose[0]))
                self.order = self.sell()

    def next(self):
        if not self.position:
            if self.rsi < 30:
                self.order = self.buy(size=100)
        else:
            if self.rsi > 70:
                self.order = self.sell(size=100)

    def stop(self):
        self.log('(MA Period, {}) Ending Value {:.2f}'.format(self.params.maperiod,self.broker.getvalue()),doprint=True)

#----------------- Analysis -------------------
def printTradeAnalysis(analyzer):   # analyzer dictionary
    total_open = analyzer.total.open   # Total trades still open
    total_closed = analyzer.total.closed   # Total closed trades
    total_won = analyzer.won.total         # Total trades won
    total_lost = analyzer.lost.total       # Total trades lost
    win_streak = analyzer.streak.won.longest    # Best winning streak
    lost_streak = analyzer.streak.lost.longest  # Worst losing streak
    pnl_net = round(analyzer.pnl.net.total, 2)  # Profit or Loss
    strike_rate = (total_won / total_closed) * 1000   #Strike rate

    h1 = ['Total Open','Total Close','Total Won','Total Lost']
    h2 = ['Strike Rate','Win Streak','Losing Streak','PnL Net']
    r1 = [total_open, total_closed, total_won, total_lost]
    r2 = [strike_rate, win_streak, lost_streak, pnl_net]

    # if len(h1) > len(h2):
    header_length = len(h1)
    # else:
        # header_length = len(h2)
    print_list = [h1, r1, h2, r2]
    row_format = "{:<15}" * (header_length + 1)
    print("Trade Analysis Results:")
    for row in print_list:
        print(row_format.format('',*row))

def printSQN(analyzer):
    sqn = round(analyzer.sqn, 2)           # SQN (System Quality Number)
    print('SQN: {}'.format(sqn))
#---------------------------------------------------------------------
if __name__ == "__main__":

    startcash = 100000000

    cerebro = bt.Cerebro()
    cerebro = bt.Cerebro(optreturn=False)   #default is OptRetun object return True

    #------------- add or opt strategy --------------------------
    cerebro.addstrategy(firstStrategy, period=14)
    cerebro.optstrategy(TestStrategy, maperiod=range(10,31))

    #------------------ Data From local file --------------------------
    datapath = 'orcl-2014.txt'

    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        fromdate = datetime.datetime(2014,1,1),
        todate=datetime.datetime(2014,12,31),
        reverse=False)
    #-------------------  direct read from stockdb ----------------------
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

    cerebro.broker.setcash(startcash)
    #------------------ Add stake size & commission -----------------------
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    # or
    cerebro.addsizer(printSizingParams)
    # or
    cerebro.addsizer(maxRiskSizer, risk=0.2)

    cerebro.broker.setcommission(commission=0.00165)           # broker commission
    #--------------- Analyzer -------------------------------------------
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")  # analyzer add to cerebro and give name for easy access

    strategies = cerebro.run()     # cerebro returns the list of strategy objects
    firstStrat = strategies[0]     # even though there's only one strategy

    printTradeAnalysis(firstStrat.analyzers.ta.get_analysis())
    printSQN(firstStrat.analyzers.sqn.get_analysis())
    #----------------- Optimize Strategy --------------------------------------
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
    #----------------- Get final Portfolio Value ------------------------
    cerebro.run()
    portvalue = cerebro.broker.getvalue()
    pnl = portvalue - startcash

    #Print out the final Result
    print('Final Portfolio Value: ${}'.format(portvalue))
    print('P/L: ${}'.format(pnl))
    #----------------- Plot result -------------------------------------
    cerebro.plot(style='candlestick')
