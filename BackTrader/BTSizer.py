import datetime
import backtrader as bt
import math

class exampleSizer(bt.Sizer):
    params = (('size', 1),)

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

class firstStrategy(bt.Strategy):

    def __init__(self):
        self.rsi = bt.indicators.RSI_SMA(self.data.close,period=21)

    def next(self):
        if not self.position:
            if self.rsi < 30:
                self.buy()
        else:
            if self.rsi > 70:
                self.sell()

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

#---------------------------------------------------------------------
if __name__ == "__main__":

    startcash = 10000

    cerebro = bt.Cerebro()

    cerebro.addstrategy(firstStrategy)

    data = bt.feeds.YahooFinanceData(
        dataname='AAPL',
        fromdate = datetime.datetime(2016,1,1),
        todate=datetime.datetime(2017,1,1),
        buffered=True)
    #------------------------------------------------------------------
    cerebro.adddata(data)

    cerebro.broker.setcash(startcash)
    #------------------ Add stake size & commission -----------------------
    cerebro.addsizer(printSizingParams)

    cerebro.run()

    portvalue = cerebro.broker.getvalue()
    pnl = portvalue - startcash

    #Print out the final Result
    print("---- Summary ----")
    print('Final Portfolio Value: ${}'.format(portvalue))
    print('P/L: ${}'.format(pnl))
    #----------------- Plot result -------------------------------------
    cerebro.plot(style='candlestick')
