import datetime
import backtrader as bt
#from collections import OrderedDict

class firstStrategy(bt.Strategy):

    def __init__(self):
        self.rsi = bt.indicators.RSI_SMA(self.data.close, period=21)

    def next(self):
        if not self.position:
            if self.rsi < 30:
                self.buy(size=100)
        else:
            if self.rsi > 70:
                self.sell(size=100)

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

def printSQN(analyzer):
    sqn = round(analyzer.sqn, 2)
    print('SQN: {}'.format(sqn))

startcash = 1000000

cerebro = bt.Cerebro()

cerebro.addstrategy(firstStrategy)

data = bt.feeds.YahooFinanceData(
    dataname="AAPL",
    fromdate = datetime.datetime(2009,1,1),
    todate=datetime.datetime(2017,1,1),
    buffered = True
    )

cerebro.adddata(data)

cerebro.broker.setcash(startcash)              # start cash

cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")

strategies = cerebro.run()
firstStrat = strategies[0]

printTradeAnalysis(firstStrat.analyzers.ta.get_analysis())
printSQN(firstStrat.analyzers.sqn.get_analysis())

portvalue = cerebro.broker.getvalue()

print('Final Portfolio Value: ${}'.format(portvalue))

cerebro.plot(style='candlestick')
