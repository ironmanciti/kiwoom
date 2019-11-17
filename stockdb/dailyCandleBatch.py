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

# Code Interval
start_code = "000000"
end_code   = "000000"

#-------------------------------------------------------------
#  일봉주가 update
def dbUpdate_Stock():
    df = pd.DataFrame(kiwoom.ohlcv, columns=['code','date','open','high','low','close','volume'])
    df.loc[:,'date'] = pd.to_datetime(df.loc[:,'date'])
    df.set_index(['date'], inplace=True)
    df.index.name = 'date'

    df.sort_index(axis=0, ascending=True, inplace=True)
    # append : insert new values to the existing table
    df.to_sql('dailycandle', con=engine, if_exists='append', \
                            dtype={'code': sqlalchemy.types.CHAR(6),
                                   'date': sqlalchemy.types.DateTime,
                                   'open': sqlalchemy.types.Integer,
                                   'high': sqlalchemy.types.Integer,
                                   'low': sqlalchemy.types.Integer,
                                   'close': sqlalchemy.types.Integer,
                                   'volume': sqlalchemy.types.Integer})

    print('code = ',kiwoom.code, ' -db updated')

# 지수 update
def dbUpdate_Market():
    df = pd.DataFrame(kiwoom.ohlcv, columns=['code','date','open','high','low','close','volume'])
    df.loc[:,'date'] = pd.to_datetime(df.loc[:,'date'])
    df.set_index(['date'], inplace=True)
    df.index.name = 'date'

    df['open']  = df['open'] / 100
    df['high']  = df['high'] / 100
    df['low']   = df['low']  / 100
    df['close'] = df['close'] / 100

    df.sort_index(axis=0, ascending=True, inplace=True)
    # replace - drop table before inserting new values
    df.to_sql('marketcandle', con=engine, if_exists='replace', \
                                        dtype={'code': sqlalchemy.types.CHAR(3),
                                               'date': sqlalchemy.types.DateTime,
                                               'open': sqlalchemy.types.Float(precision=2, asdecimal=True),
                                               'high': sqlalchemy.types.Float(precision=2, asdecimal=True),
                                               'low': sqlalchemy.types.Float(precision=2, asdecimal=True),
                                               'close': sqlalchemy.types.Float(precision=2, asdecimal=True),
                                               'volume': sqlalchemy.types.Integer})

    print('code = ',kiwoom.code, ' -db updated')

def process_stock_transaction():   #opt10081 주식일봉차트요청

    cnt = 0
    while kiwoom.remained_data == True:

        time.sleep(TR_REQ_TIME_INTERVAL)

        kiwoom.set_input_value("종목코드", kiwoom.code)
        kiwoom.set_input_value("기준일자", end_date)
        kiwoom.set_input_value("수정주가구분", 1)
        if cnt > 0:
            next = 2
        else:
            next = 0
        kiwoom.comm_rq_data("opt10081_req", "opt10081", next, "0101")
        cnt += 1

def process_market_transaction():      #opt20006 업종일봉조회요청
    # 업종코드 = 001:종합(KOSPI), 002:대형주, 003:중형주, 004:소형주 101:종합(KOSDAQ), 201:KOSPI200
    # 기준일자 = YYYYMMDD (20160101 연도4자리, 월 2자리, 일 2자리 형식)
    cnt = 0
    while kiwoom.remained_data == True:

        time.sleep(TR_REQ_TIME_INTERVAL)

        kiwoom.set_input_value("업종코드", kiwoom.code)
        kiwoom.set_input_value("기준일자", end_date)
        if cnt > 0:
            next = 2
        else:
            next = 0
        kiwoom.comm_rq_data("opt20006_req", "opt20006", next, "0202")
        cnt += 1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.comm_connect()

    if len(sys.argv) < 7:
        print("Arguments should be 1 : 20006 or 10081, 2: start_code, 3: end_code, 4: market_code ")
        print("          in case of 20006, start_code=000000, end_code=999999, market_code=0, end_date=999999")
        print("          in case of 10081, start_code / end_code / market_code /end_date / kospi_200 should be given.")
        print(sys.argv)
        quit()
    elif sys.argv[1] not in ["20006", "10081"]:
        print("Invalid TR Code")
        quit()
    else:
        tr_code    = str(sys.argv[1]).zfill(5)
        start_code = str(sys.argv[2]).zfill(6)
        end_code   = str(sys.argv[3]).zfill(6)
        market_code = str(sys.argv[4]) # 0: KOSPI, 3: ELW, 10: KOSDAQ, 8:ETF
        end_date = str(sys.argv[5]) # 기준일자
        kospi_200 = str(sys.argv[6]) # 1: kospi200 only, 0: all 종목
        print("arguments")
        print("tr_code =", tr_code)
        print("start_code =", start_code)
        print("end_code = ", end_code)
        print("market_code =", market_code)
        print("end_date =", end_date)
        print("kospi_200 =", kospi_200)

    if tr_code == "20006": # tr code 20006 - 업종일봉조회

        batch_codes = ["001", "002", "003", "004", "101", "201"]
        kiwoom.ohlcv = {'code': [], 'date': [], 'open': [], 'high': [], 'low': [], \
                        'close': [], 'volume': []}

        for code in batch_codes:
            time.sleep(TR_REQ_TIME_INTERVAL)
            kiwoom.code = code
            kiwoom.remained_data = True
            process_market_transaction()
            dbUpdate_Market()

        print("last updated code = ", code)

    elif tr_code == "10081":  # tr code 10081 - 주식일봉차트요청
        if start_code == end_code == '201777':  # KOSPI200 에 속하면서 fscore 7 이상인 종목만 처리
            batch_codes = pd.read_sql("select code from stockcode where kospi200 = true and fscore >= 7", conn)['code'].tolist()
        elif start_code <= end_code:
            if kospi_200 == '1':
                batch_codes = pd.read_sql("select code from stockcode where smarket = '" + market_code +\
                                          "' and code >= '" + start_code + "' and code <= '" + end_code +
                                          "' and kospi200 = '" + kospi_200 +\
                                          "' order by code asc", con=engine)['code'].tolist()
            else: # kospi_200 = '0'
                batch_codes = pd.read_sql("select code from stockcode where smarket = '" + market_code +\
                                          "' and code >= '" + start_code + "' and code <= '" + end_code + "'\
                                          order by code asc", con=engine)['code'].tolist()
        else:
            print("invalid start/end_code")
            print("start_code = ", start_code, "end_code = ", end_code)
            quit()

        process_cnt = 0

        if len(batch_codes) > 0:

            for code in batch_codes:
                if process_cnt > 50:
                    time.sleep(TR_REQ_SLEEP_INTERVAL)
                    process_cnt = 0

                time.sleep(TR_REQ_TIME_INTERVAL)
                kiwoom.ohlcv = {'code': [], 'date': [], 'open': [], 'high': [], 'low': [], \
                                'close': [], 'volume': []}
                kiwoom.code = code
                kiwoom.remained_data = True
                process_stock_transaction()

                process_cnt += 1
                #dbUpdate_Stock()
                print("process_cnt = ",process_cnt)
        else:
            print("no code for ", start_code, end_code)

    conn.close()
