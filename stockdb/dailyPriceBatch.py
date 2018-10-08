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
def delete_dailyprice(code):
    sql = "DELETE from dailyprice WHERE code = '" + code + "'"
    try:
        with con.cursor() as cursor:
            cursor.execute(sql)
        con.commit()
        print('deleted code = ',code, ' -table records deleted')
    finally:
        con.close()

def dbUpdate_dailyprice():
    df = pd.DataFrame(kiwoom.dailyprice, columns=['code','date','open','high','low','close','volume',
                                                'credit_ratio', 'foreigner_net_buy', 'inst_net_buy'])
    df.loc[:,'date'] = pd.to_datetime(df.loc[:,'date'])
    df.set_index(['date'], inplace=True)
    df.index.name = 'date'

    df.sort_index(axis=0, ascending=True, inplace=True)
    # append : insert new values to the existing table
    df.to_sql('dailyprice', con=engine, if_exists='append', \
                            dtype={'code': sqlalchemy.types.CHAR(6),
                                   'date': sqlalchemy.types.DateTime,
                                   'open': sqlalchemy.types.Integer,
                                   'high': sqlalchemy.types.Integer,
                                   'low': sqlalchemy.types.Integer,
                                   'close': sqlalchemy.types.Integer,
                                   'volume': sqlalchemy.types.Integer,
                                   'credit_ratio': sqlalchemy.types.Float(precision=2, asdecimal=True),
                                   'foreigner_net_buy': sqlalchemy.types.Integer,
                                   'inst_net_buy': sqlalchemy.types.Integer,
                                   })

    print('code = ',kiwoom.code, ' -db updated')

def process_dailyprice_transaction():   #opt10086  # 일별주가요청(multi-data)

    cnt = 0
    while kiwoom.remained_data == True:

        time.sleep(TR_REQ_TIME_INTERVAL)

        kiwoom.set_input_value("종목코드", kiwoom.code)
        kiwoom.set_input_value("조회일자", end_date)
        kiwoom.set_input_value("표시구분", 0)    # 0: 수량, 1: 금액(백만원)
        if cnt > 0:
            next = 2
        else:
            next = 0
        kiwoom.comm_rq_data("opt10086_req", "opt10086", next, "0101")
        cnt += 1


if __name__ == "__main__":
    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.comm_connect()

    # Code Interval
    start_code = "000660"  # '005380'-현대차, '005930'-삼성전자, '051910'-LG화학, '035420'-NAVER, '030200'-KT, '000660'-SK하이닉스
    #end_code   = "030200"
    end_date = "20180901"

#    start_code = str(sys.argv[1]).zfill(6)
#    end_code   = str(sys.argv[2]).zfill(6)
#    start_date = str(sys.argv[3])            # 시작일자
    print("arguments")
    print("start_code =", start_code)
    #print("end_code =", end_code)
    print("end_date =", end_date)

    delete_dailyprice(start_code)

    process_cnt = 0
    #
    # if process_cnt > 50:
    #     time.sleep(TR_REQ_SLEEP_INTERVAL)
    #     process_cnt = 0

    time.sleep(TR_REQ_TIME_INTERVAL)
    kiwoom.dailyprice = {'code': [], 'date': [], 'open': [], 'high': [], 'low': [], \
                        'close': [], 'volume': [], 'credit_ratio': [], 'foreigner_net_buy': [],
                        'inst_net_buy': []}
    kiwoom.code = start_code
    kiwoom.remained_data = True
    process_dailyprice_transaction()

    process_cnt += 1
    dbUpdate_dailyprice()
    print("process_cnt = ",process_cnt)

    conn.close()
