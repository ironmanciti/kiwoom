import backtrader as bt
import backtrader.indicators as btind
import datetime
import pandas as pd
import pickle
import math
from sklearn.linear_model import LogisticRegression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis as QDA
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier

class LAPS(bt.Strategy):

    def log(self, txt, dt=None, doprint=True):
        if doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        """Initialize the strategy"""

        self._addobserver(True, bt.observers.BuySell)    # CAUTION: Abuse of the method, I will change this in future code (see: https://community.backtrader.com/topic/473/plotting-just-the-account-s-value/4)

    def next(self):
        """Define what will be done in a single step, including creating and closing trades"""
        d = self.getdatanames()[0]

        features = self.getdatabyname(d).features
        model = self.getdatabyname(d).model
        predict = 0

        if self.datas[0].datetime.date(0) in features.index:
            pred = model.predict([features.loc[self.datas[0].datetime.date(0)]])
            predict = pred[0]
            self.log('predIct = {}'.format(predict))

        pos = self.getpositionbyname(d).size or 0
        if pos == 0:    # Are we out of the market?
            if predict > 0:    # A buy signal
                self.buy(data=self.getdatabyname(d))
                self.getdatabyname(d).total_buy += 1
        else:    # We have an open position
            if predict < 0:    # A sell signal
                self.sell(data=self.getdatabyname(d))
                self.log('sell')
                self.getdatabyname(d).total_sell += 1


class PropSizer(bt.Sizer):
    """A position sizer that will buy as many stocks as necessary for a certain proportion of the portfolio
       to be committed to the position, while allowing stocks to be bought in batches (say, 100)"""
    params = {"prop": 0.9, "batch": 1}

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
        self._owner.log("today's value = {:.0f}".format(self._owner.broker.getvalue()))

def printTradeAnalysis(analyzer):
    total_open = analyzer.total.open
    total_closed = analyzer.total.closed
    total_won = analyzer.won.total
    total_lost = analyzer.lost.total
    win_streak = analyzer.streak.won.longest
    lose_streak = analyzer.streak.lost.longest
    pnl_net = round(analyzer.pnl.net.total, 2)
    strike_rate = (total_won / total_closed) * 100

    h1 = ['Total Open','Total Close','Total Won','Total Lost']
    h2 = ['Strike Rate','Win Streak','Losing Streak','PnL Net']
    r1 = [total_open, total_closed, total_won, total_lost]
    r2 = [strike_rate, win_streak, lose_streak, pnl_net]

    header_length = len(h1)

    print_list = [h1, r1, h2, r2]
    row_format = "{:<15}" * (header_length + 1)
    print("Trade Analysis Results:")
    for row in print_list:
        print(row_format.format('',*row))

startcash = 100000000

cerebro = bt.Cerebro(stdstats=False)    # I don't want the default plot objects

cerebro.broker.set_cash(startcash)    # Set our starting cash to $1,000,000
cerebro.broker.setcommission(0.00)

#-------------------------------------------------
fromdate = datetime.datetime(2017, 1, 1)
todate = datetime.datetime(2018, 3, 30)
#--------------------------------------------
import sys
sys.path.append('../lib/')
from makeKospi200Data import *

start_test = '2017-01-01'
start_validation = '2018-03-30'
end_date = '2018-03-30'
code = '201'
pickle_path = '..\\dataOutput\\'

with open(pickle_path + 'GTB-2018-04-09-9-13_model_for_backtest.pickle', 'rb') as f:
        clf = pickle.load(f)

model = clf['model']

win_K   = clf['win_K']
win_CCI = clf['win_CCI']
win_R   = clf['win_R']
lag      = clf['lag']
RSI_span = clf['RSI_span']
win_ma   = clf['win_ma']
method   = clf['method']

#------------------------------------
_, X, _, _, _, _ \
    = make_data(end_date, start_test, start_validation, code, win_K, win_CCI, win_R, lag, RSI_span, win_ma)

X.index = pd.to_datetime(X.index)

#-------------------  direct read from stockdb ----------------------
market_code = '201'
fromdate = datetime(2017,1,1)
todate   = datetime(2018,3,30)
KOSPI200 = pd.read_sql("SELECT * from marketcandle where code= {} and date between '{}' \
                        and '{}'".format(market_code, fromdate, todate), con=engine, index_col=["date"])
KOSPI200['openinterest'] = 0
KOSPI200.drop(['code'], axis=1,inplace=True);

KOSPI200_start_close = KOSPI200.ix[0,'close']
KOSPI200_end_close   = KOSPI200.ix[-1,'close']

data = bt.feeds.PandasData(dataname=KOSPI200)

data.features = X
data.model = model
data.total_buy = 0
data.total_sell = 0

cerebro.adddata(data)    # Give the data to cerebro

cerebro.addobserver(AcctValue)
cerebro.addstrategy(LAPS)
cerebro.addsizer(PropSizer)
#cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")

cerebro.broker.getvalue()

strategies = cerebro.run()

cerebro.plot(iplot=True, volume=False)

firstStrat = strategies[0]
#printTradeAnalysis(firstStrat.analyzers.ta.get_analysis())

portvalue = cerebro.broker.getvalue()
pnl = math.floor(portvalue - startcash)
days = (todate - fromdate).days
rate = pnl / startcash * 365 / days  * 100

rate_KOSPI200 = (KOSPI200_end_close - KOSPI200_start_close) / KOSPI200_start_close * 365 / days * 100

diff = rate - rate_KOSPI200

#Print out the final Result
print('Portpolid Value: {0:,} P/L: KRW {1:,}'.format(portvalue, pnl))
print('P/L: KRW {0:,}  Annualized Rate: {1:.2f} %'.format(pnl, rate))
print('       KOSPI200 Annualized Rate: {0:.2f} %'.format(rate_KOSPI200))
print('                     Difference: {0:.2f} %'.format(diff))

print('total buy = ',data.total_buy)
print('total sell = ',data.total_sell)

#Finally plot the end results
#cerebro.plot(style='candlestick')
