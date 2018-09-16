import backtrader as bt
import backtrader.indicators as btind
import datetime
import pandas as pd
from pandas import Series, DataFrame
import random
from copy import deepcopy
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis as QDA
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier

class SMAC(bt.Strategy):
    """A simple moving average crossover strategy; crossing of a fast and slow moving average generates buy/sell
       signals"""
    params = {"fast": 20, "slow": 50,                  # The windows for both fast and slow moving averages
              "optim": False, "optim_fs": (20, 50)}    # Used for optimization; equivalent of fast and slow, but a tuple
                                                       # The first number in the tuple is the fast MA's window, the
                                                       # second the slow MA's window
    def log(self, txt, dt=None, doprint=True):
        if doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))


    def __init__(self):
        """Initialize the strategy"""

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
            close = self.getdatabyname(d).close[0]
            lags = self.getdatabyname(d).lags
            model = self.getdatabyname(d).model

            #self.log('tdate = ' + str(self.datas[0].datetime.date(0)))
            if self.datas[0].datetime.date(0) in lags.index:
                pred = model.predict([lags.loc[self.datas[0].datetime.date(0)]])
                self.log('pred= {0:.2f}'.format(pred[0]))

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

class AcctStats(bt.Analyzer):
    """A simple analyzer that gets the gain in the value of the account; should be self-explanatory"""

    def __init__(self):
        self.start_val = self.strategy.broker.get_value()
        self.end_val = None

    def stop(self):
        self.end_val = self.strategy.broker.get_value()

    def get_analysis(self):
        return {"start": self.start_val, "end": self.end_val,
                "growth": self.end_val - self.start_val, "return": self.end_val / self.start_val}

class AcctValue(bt.Observer):
    alias = ('Value',)
    lines = ('value',)

    plotinfo = {"plot": True, "subplot": True}

    def next(self):
        self.lines.value[0] = self._owner.broker.getvalue()    # Get today's account value (cash + stocks)

cerebro = bt.Cerebro(stdstats=False)    # I don't want the default plot objects

cerebro.broker.set_cash(1000000)    # Set our starting cash to $1,000,000
cerebro.broker.setcommission(0.02)

#-------------------------------------------------
start = datetime.datetime(2018, 1, 1)
end = datetime.datetime(2018, 3, 31)
#--------------------------------------------
import sys
sys.path.append('../lib/')
from makeData import *

start_test = '2018-01-01'
start_validation = '2018-01-01'
data_path   = '..\\dataBackTesting\\'
pickle_path = '..\\dataOutput\\'

with open(pickle_path + 'LDA-2018-03-29-5-6_model_for_backtest.pickle', 'rb') as f:
        clf = pickle.load(f)

model = clf['model']
lag   = clf['lag']
delta = clf['delta']
#------------------------------------

is_first = True

symbols = ['^AXJO', '^DJI', '^FCHI', '^HSI', '^N225', '^IXIC', '^GDAXI','SPY']

#symbols = ["AXJO", "DJI", "FCHI", "HSI", "N225", "IXIC", "GDAXI", "SPY"]
plot_symbols = ['^AXJO', '^DJI', '^FCHI']

_, _, X, _, _, _ \
    = make_data(lag, delta, start_test, start_validation, data_path, symbols)

X.index = pd.to_datetime(X.index)

for d in symbols:

    ohlc = pd.read_csv(data_path + d + '.csv', header=0, \
            names=['date','open','high','low','close','adj close','volume'])
    ohlc.loc[:,'date'] = pd.to_datetime(ohlc.loc[:,'date'])
    ohlc.set_index(['date'], inplace=True)

    data = bt.feeds.PandasData(dataname=ohlc)

    data.lags = X
    data.model = model

    if d in plot_symbols:
       if is_first:
           data_main_plot = data
           is_first = False
       else:
           data.plotinfo.plotmaster = data_main_plot
    else:
       data.plotinfo.plot = False

    cerebro.adddata(data)    # Give the data to cerebro

#start = datetime.datetime(2010, 1, 1)

cerebro.addobserver(AcctValue)
cerebro.addstrategy(SMAC)
cerebro.addsizer(PropSizer)

cerebro.broker.getvalue()

cerebro.run()

cerebro.plot(iplot=True, volume=False)

cerebro.broker.getvalue()
