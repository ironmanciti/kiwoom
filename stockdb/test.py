from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import pandas as pd
import sqlalchemy
import time
import sys
sys.path.append('../lib/')

from dbConnect import *
from kiwoomMain import *

#---------------------------- Input Parameters ------------------
# Time Sleep parameter
TR_REQ_TIME_INTERVAL = 0.55
TR_REQ_SLEEP_INTERVAL = 60

#-------------------------------------------------------------
#  일봉주가 update

def process_stock_transaction():   #opt10081 주식일봉차트요청

    cnt = 0
    while kiwoom.remained_data == True:

        time.sleep(TR_REQ_TIME_INTERVAL)

        kiwoom.set_input_value("종목코드", "039490")
        kiwoom.set_input_value("기준일자", "20170224")
        kiwoom.set_input_value("수정주가구분", 1)
        if cnt > 0:
            next = 2
        else:
            next = 0
        kiwoom.comm_rq_data("opt10081_req", "opt10081", next, "0101")
        cnt += 1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.comm_connect()

    kiwoom.ohlcv = {'code': [], 'date': [], 'open': [], 'high': [], 'low': [], \
                    'close': [], 'volume': []}
    kiwoom.remained_data = True
    process_stock_transaction()


