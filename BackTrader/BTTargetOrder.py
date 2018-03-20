from datetime import datetime
import backtrader as bt
import argparse

import pandas as pd

import sys
sys.path.append('../lib/')
from dbConnect import *

class TheStrategy(bt.Strategy):

    params = (
        ('use_target_size', False),
        ('use_target_value', False),
        ('use_target_percent', False),
    )

    def notify_order(self, order):
        if order.status == order.Completed:
            pass

        if not order.alive():
            self.order = None                    # pending 되어 있는 order 가 없음 표시

    def start(self):
        self.order = None           # sentinel to avoid operations to pending order

    def next(self):
        dt = self.data.datetime.date()

        portfolio_value = self.broker.get_value()
        print("{} - {} - Position Size:  {} -- value {:.2f}"
                .format(len(self), dt.isoformat(),self.position.size, portfolio_value))

        data_value = self.broker.get_value([self.data])
        print(self.data)

        if self.p.use_target_value:
            print('%04d - %s - data value %.2f' %
                  (len(self), dt.isoformat(), data_value))

        elif self.p.use_target_percent:
            port_perc = data_value / portfolio_value
            print('%04d - %s - data percent %.2f' %
                  (len(self), dt.isoformat(), port_perc))

        if self.order:
            return  # pending order execution

        size = 30
        # size = dt.day
        # if (dt.month % 2) == 0:
        #     size = 31 - size

        if self.p.use_target_size:
            target = size
            print('%04d - %s - Order Target Size: %02d' %
                  (len(self), dt.isoformat(), size))

            self.order = self.order_target_size(target=size)

        elif self.p.use_target_value:
            value = size * 1000

            print('%04d - %s - Order Target Value: %.2f' %
                  (len(self), dt.isoformat(), value))

            self.order = self.order_target_value(target=value)

        elif self.p.use_target_percent:
            percent = size / 100.0

            print('%04d - %s - Order Target Percent: %.2f' %
                  (len(self), dt.isoformat(), percent))

            self.order = self.order_target_percent(target=percent)

def runstrat(args=None):
    args = parse_args(args)

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(args.cash)

    if args.target_percent == True:
        args.target_percent = 0.3

    code = args.code
    fromdate = datetime.strptime(args.fromdate, '%Y-%m-%d')
    todate   = datetime.strptime(args.todate, '%Y-%m-%d')
    db_frame = pd.read_sql("SELECT * from dailycandle where code = {} and date between '{}' \
                            and '{}'".format(code, fromdate, todate), con=engine, index_col=["date"])
    db_frame['openinterest'] = 0
    db_frame.drop(['code'], axis=1,inplace=True);
    data = bt.feeds.PandasData(dataname=db_frame)

    cerebro.adddata(data)

    # strategy
    cerebro.addstrategy(TheStrategy,
                        use_target_size=args.target_size,
                        use_target_value=args.target_value,
                        use_target_percent=args.target_percent)

    print("$$$args ==", args)

    cerebro.run()

    # if args.plot:
    #     pkwargs = dict(style='bar')
    #     if args.plot is not True:  # evals to True but is not True
    #         npkwargs = eval('dict(' + args.plot + ')')  # args were passed
    #         pkwargs.update(npkwargs)
    #
    #     cerebro.plot(**pkwargs)

def parse_args(pargs=None):

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Sample for Order Target')

    parser.add_argument('--code', required=False,
                        default='005930',
                        help='Specific stock code to be read in')

    parser.add_argument('--fromdate', required=False,
                        default='2005-01-01',
                        help='Starting date in YYYY-MM-DD format')

    parser.add_argument('--todate', required=False,
                        default='2006-12-31',
                        help='Ending date in YYYY-MM-DD format')

    parser.add_argument('--cash', required=False, action='store',
                        type=float, default=1000000,
                        help='Ending date in YYYY-MM-DD format')

    pgroup = parser.add_mutually_exclusive_group(required=True)

    pgroup.add_argument('--target-size', required=False, action='store_true',
                        help=('Use order_target_size'))

    pgroup.add_argument('--target-value', required=False, action='store_true',
                        help=('Use order_target_value'))

    pgroup.add_argument('--target-percent', required=False, action='store_true',
                        help=('Use order_target_percent'))

    #Plot options
    parser.add_argument('--plot', '-p', nargs='?', required=False,
                        metavar='kwargs', const=True,
                        help=('Plot the read data applying any kwargs passed\n'
                              '\n'
                              'For example:\n'
                              '\n'
                              '  --plot style="candle" (to plot candles)\n'))

    if pargs is not None:
        return parser.parse_args(pargs)

    return parser.parse_args()


if __name__ == '__main__':
    runstrat()
