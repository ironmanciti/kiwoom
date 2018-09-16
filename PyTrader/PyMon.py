import sys
from PyQt5.QtWidgets import *
import pandas as pd
import time
import datetime

sys.path.append('../lib/')

from kiwoomMain import *

MARKET_KOSPI = 0
MARKET_KOSDAQ = 10
TR_REQ_TIME_INTERVAL = 0.55
TR_REQ_SLEEP_INTERVAL = 30 

class PyMon:
    def __init__(self):
        self.kiwoom = Kiwoom()
        self.kiwoom.comm_connect()
        self.get_code_list()

    def get_code_list(self):
        self.kospi_codes = self.kiwoom.get_code_list_by_market(MARKET_KOSPI)
        self.kosdaq_codes = self.kiwoom.get_code_list_by_market(MARKET_KOSDAQ)

    def get_ohlcv(self, code, start):
        self.kiwoom.ohlcv = {'code':[], 'date':[], 'open':[], 'high':[], 'low':[],
                             'close':[], 'volume':[]}
        self.kiwoom.code = code
        self.kiwoom.set_input_value("종목코드", code)
        self.kiwoom.set_input_value("기준일자", start)
        self.kiwoom.set_input_value("수정주가구분", "1")
        self.kiwoom.comm_rq_data("opt10081_req", "opt10081", 0, "0101")
        time.sleep(TR_REQ_TIME_INTERVAL)
        df = pd.DataFrame(self.kiwoom.ohlcv, columns=['open', 'high', 'low', 'close', 
                                            'volume'], index=self.kiwoom.ohlcv['date'])
        return df
    
    def check_speedy_rising_volume(self, code):  # 급등주 발견 알고리즘
        today = datetime.datetime.today().strftime('%Y%m%d')
        df = self.get_ohlcv(code, today)
        volumes = df['volume']
        
        if len(volumes) < 21:
            return False
        
        sum_vol20 = 0
        today_vol = 0
        
        for i, vol in enumerate(volumes):
            if i == 0:
                today_vol = vol
            elif i >= 1 and i <= 20:
                sum_vol20 += vol
            else:
                break
        
        avg_vol20 = sum_vol20 / 20
        if today_vol >= avg_vol20 * 10:
            return True

    def write_buy_list(self, buy_list):  # 일괄매수주문 file 작성
        f = open("buy_list.txt", "wt")
        for market, codelist in buy_list.items():
            if market == 'kospi':
                for code in codelist:
                    f.write("매수;" + code + ";시장가;0;0;매수전\n")
                    print("매수;" + code + ";시장가;0;0;매수전")
            elif market == 'kosdaq':
                for code in codelist:
                    f.write("매수;" + code + ";시장가;10;0;매수전\n")
                    print("매수;" + code + ";시장가;10;0;매수전")
            else:
                print('invalid market gubun')
                return
        f.close()
            
    def update_buy_list(self, code_list, buy_list, market):
        
        num = len(code_list)
        
        process_cnt = 0
        
        for i, code in enumerate(code_list):
            print("{} / {}".format(code, num))
            
            process_cnt += 1
            if process_cnt > 100:
                self.kiwoom.comm_connect()
                process_cnt = 0
                
            if self.check_speedy_rising_volume(code):
                buy_list[market].append(code)
        
    def run(self):
        buy_list = {'kospi': [], 'kosdaq': []}

        self.update_buy_list(self.kospi_codes, buy_list, 'kospi')
        self.update_buy_list(self.kosdaq_codes, buy_list, 'kosdaq')
        
        self.write_buy_list(buy_list)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pymon = PyMon()
    pymon.run()