import datetime
import backtrader as bt
import backtrader.indicators as btind
import pandas as pd
from pandas import Series, DataFrame
import random
from copy import deepcopy
import sys
import pandas as pd
sys.path.append('../lib/')
from dbConnect import *

class SMAC(bt.Strategy):
    """A simple moving average crossover strategy; crossing of a fast and slow moving average generates buy/sell
       signals"""
    params = {"fast": 20, "slow": 50,                  # The windows for both fast and slow moving averages
              "optim": False, "optim_fs": (20, 50)}    # Used for optimization; equivalent of fast and slow, but a tuple
                                                       # The first number in the tuple is the fast MA's window, the
                                                         # second the slow MA's window
    def __init__(self):

        self.fastma = dict()
        self.slowma = dict()
        self.regime = dict()

        self._addobserver(True, bt.observers.BuySell)    # CAUTION: Abuse of the method, I will change this in future code (see: https://community.backtrader.com/topic/473/plotting-just-the-account-s-value/4)

        if self.params.optim:    # Use a tuple during optimization
            self.params.fast, self.params.slow = self.params.optim_fs    # fast and slow replaced by tuple's contents

        if self.params.fast > self.params.slow:
            raise ValueError(
                "A SMAC strategy cannot have the fast moving average's window be " + \
                 "greater than the slow moving average window.")

        for d in self.getdatanames():

            # The moving averages
            self.fastma[d] = btind.SimpleMovingAverage(self.getdatabyname(d),      # The symbol for the moving average
                                                       period=self.params.fast,    # Fast moving average
                                                       plotname="FastMA: " + d)
            self.slowma[d] = btind.SimpleMovingAverage(self.getdatabyname(d),      # The symbol for the moving average
                                                       period=self.params.slow,    # Slow moving average
                                                       plotname="SlowMA: " + d)

            # Get the regime
            self.regime[d] = self.fastma[d] - self.slowma[d]    # Positive when bullish

    def next(self):
        """Define what will be done in a single step, including creating and closing trades"""
        for d in self.getdatanames():    # Looping through all symbols
            pos = self.getpositionbyname(d).size or 0
            if pos == 0:    # Are we out of the market?
                # Consider the possibility of entrance
                # Notice the indexing; [0] always mens the present bar, and [-1] the bar immediately preceding
                # Thus, the condition below translates to: "If today the regime is bullish (greater than
                # 0) and yesterday the regime was not bullish"
                if self.regime[d][0] > 0 and self.regime[d][-1] <= 0:    # A buy signal
                    self.buy(data=self.getdatabyname(d))

            else:    # We have an open position
                if self.regime[d][0] <= 0 and self.regime[d][-1] > 0:    # A sell signal
                    self.sell(data=self.getdatabyname(d))

class PropSizer(bt.Sizer):
    """A position sizer that will buy as many stocks as necessary for a certain proportion of the portfolio
       to be committed to the position, while allowing stocks to be bought in batches (say, 100)"""
    params = {"prop": 0.1, "batch": 100}

    def _getsizing(self, comminfo, cash, data, isbuy):
        """Returns the proper sizing"""

        if isbuy:    # Buying
            target = self.broker.getvalue() * self.params.prop    # Ideal total value of the position
            price = data.close[0]
            shares_ideal = target / price    # How many shares are needed to get target
            batches = int(shares_ideal / self.params.batch)    # How many batches is this trade?
            shares = batches * self.params.batch    # The actual number of shares bought

            if shares * price > cash:
                return 0    # Not enough money for this trade
            else:
                return shares

        else:    # Selling
            return self.broker.getposition(data).size    # Clear the position

class AcctValue(bt.Observer):
    alias = ('Value',)
    lines = ('value',)

    plotinfo = {"plot": True, "subplot": True}

    def next(self):
        self.lines.value[0] = self._owner.broker.getvalue()    # Get today's account value (cash + stocks)

#---------------------------------------------------------------------

cerebro = bt.Cerebro(stdstats=False)    # I don't want the default plot objects
cerebro.broker.set_cash(1000000)    # Set our starting cash to $1,000,000
cerebro.broker.setcommission(0.02)

cerebro.addobserver(AcctValue)
cerebro.addstrategy(SMAC)
cerebro.addsizer(PropSizer)



start = datetime.datetime(2010, 1, 1)
end = datetime.datetime(2016, 10, 31)
is_first = True
# Not the same set of symbols as in other blog posts
symbols = ["AAPL", "GOOG", "MSFT", "AMZN", "YHOO", "SNY", "NTDOY", "IBM", "HPQ", "QCOM", "NVDA"]
plot_symbols = ["AAPL", "GOOG", "NVDA"]
#plot_symbols = []
for s in symbols:
    data = bt.feeds.YahooFinanceData(dataname=s, fromdate=start, todate=end)
    if s in plot_symbols:
        if is_first:
            data_main_plot = data
            is_first = False
        else:
            data.plotinfo.plotmaster = data_main_plot
    else:
        data.plotinfo.plot = False
    cerebro.adddata(data)    # Give the data to cerebro

cerebro.run()


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

    cerebro.broker.set_cash(1000000)    # Set our starting cash to $1,000,000
cerebro.broker.setcommission(0.02)
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
