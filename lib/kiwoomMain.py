#직접 수행 혹은  다른 프로그램에서 import kiwoomMain 하여 사용
#from kiwoomMain import *
#dict = kiwoomMain.dailyCandle(code) - 종목코드
#df = pd.DataFrame.from_dict(dict) - DataFrame 반환

import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import pandas as pd
import time

TR_REQ_TIME_INTERVAL = 0.2

class Kiwoom(QAxWidget):

    def __init__(self):
        super().__init__()
        self._create_kiwoom_instance()
        self._set_signal_slots()

        # self.remained_data = True
        # self.ohlcv = {'code': [], 'date': [], 'open': [], 'high': [], 'low': [], \
        #                 'close': [], 'volume': []}

    def _create_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1") #---> kiwoom's ProgID registered in windows registry

    def _set_signal_slots(self):
        self.OnEventConnect.connect(self._event_connect)
        self.OnReceiveTrData.connect(self._receive_tr_data)
        self.OnReceiveChejanData.connect(self._receive_chejan_data)

    def comm_connect(self):
        self.dynamicCall("CommConnect()")      # --> execute login window
        self.login_event_loop = QEventLoop()   #--> create instance using QEventLoop class of PyQt
        self.login_event_loop.exec_()          # --> call exec_ method of the instance

    def _event_connect(self, err_code):
        if err_code == 0:
            print("connected")
        else:
            print("disconnected")

        self.login_event_loop.exit()

    def get_code_list_by_market(self, market):
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market)   # call Kiwoom method
        code_list = code_list.split(';')
        return code_list[:-1]

    def get_master_code_name(self, code):
        code_name = self.dynamicCall("GetMasterCodeName(QString)", code)
        return code_name

    def get_server_gubun(self):
        ret = self.dynamicCall("KOA_Functions(QString, QString)", "GetServerGubun", "")
        return ret

    def get_chejan_data(self, fid):
        ret = self.dynamicCall("GetChejanData(int)", fid)
        return ret

    def get_login_info(self, tag):
        ret = self.dynamicCall("GetLoginInfo(QString)", tag)
        return ret

    def send_order(self, rqname, screen_no, acc_no, order_type, code, quantity, price, hoga, order_no):
        self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", \
                        [rqname, screen_no, acc_no, order_type, code, quantity, price, hoga, order_no])

    def get_connect_state(self):
        ret = self.dynamicCall("GetConnectState()")
        return ret

    def set_input_value(self, id, value):
        self.dynamicCall("SetInputValue(QString, QString)", id, value)

    def comm_rq_data(self, rqname, trcode, next, screen_no):
        self.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, trcode, next, screen_no)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

    def _get_comm_data(self, trcode, rqname, index, item_name):
        ret = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, index, item_name)
        return ret.strip()

    def _get_repeat_cnt(self, trcode, rqname):
        ret = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

    def _receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, ununsed2, unused3, unused4):
        if next == '2':
            self.remained_data = True
        else:
            self.remained_data = False

        if rqname == "opw00001_req":    #예수금상세현황요청
            self._opw00001(rqname, trcode)

        if rqname == "opw00018_req":    #계좌평가잔고내역요청
            self._opw00018(rqname, trcode)

        if rqname == "opt10081_req":    #주식일봉차트요청(종목코드/기준일자/수정주가구분)
            self._opt10081(rqname, trcode)

        if rqname == "opt20001_req":    #업종현재가요청(시장구분/업종코드)
            self._opt10081(rqname, trcode)  # opt10081 과 처리 logic 공유

        if rqname == "opt20006_req":    #업종일봉조회요청(업종코드/기준일자)
            self._opt20006(rqname, trcode)

        try:
            self.tr_event_loop.exit()
        except AttributeError:
            pass

    def _receive_chejan_data(self, gubun, item_cnt, fid_list):
        print(gubun)
        print(self.get_chejan_data(9203))
        print(self.get_chejan_data(302))
        print(self.get_chejan_data(900))
        print(self.get_chejan_data(901))

    def _opw00001(self, rqname, trcode):
        d2_deposit = self._get_comm_data(trcode, rqname, 0, "d+2추정예수금")
        self.d2_deposit = Kiwoom.change_format(d2_deposit)

    def reset_opw00018_output(self):
        self.opw00018_output = {'single': [], 'multi': []}

    def _opw00018(self, rqname, trcode):
        # single data
        total_purchase_price = self._get_comm_data(trcode, rqname, 0, "총매입금액")
        total_eval_price = self._get_comm_data(trcode, rqname, 0, "총평가금액")
        total_eval_profit_loss_price = self._get_comm_data(trcode, rqname, 0, "총평가손익금액")
        total_earning_rate = self._get_comm_data(trcode, rqname, 0, "총수익률(%)")
        estimated_deposit = self._get_comm_data(trcode, rqname, 0, "추정예탁자산")

        self.opw00018_output['single'].append(Kiwoom.change_format(total_purchase_price))
        self.opw00018_output['single'].append(Kiwoom.change_format(total_eval_price))
        self.opw00018_output['single'].append(Kiwoom.change_format(total_eval_profit_loss_price))

        total_earning_rate = Kiwoom.change_format(total_earning_rate)

        if self.get_server_gubun():
            total_earning_rate = float(total_earning_rate) / 100
            total_earning_rate = str(total_earning_rate)

        self.opw00018_output['single'].append(total_earning_rate)

        self.opw00018_output['single'].append(Kiwoom.change_format(estimated_deposit))

        # multi data
        rows = self._get_repeat_cnt(trcode, rqname)
        for i in range(rows):
            name = self._comm_get_data(trcode, "", rqname, i, "종목명")
            quantity = self._comm_get_data(trcode, "", rqname, i, "보유수량")
            purchase_price = self._comm_get_data(trcode, "", rqname, i, "매입가")
            current_price = self._comm_get_data(trcode, "", rqname, i, "현재가")
            eval_profit_loss_price = self._comm_get_data(trcode, "", rqname, i, "평가손익")
            earning_rate = self._comm_get_data(trcode, "", rqname, i, "수익률(%)")

            quantity = Kiwoom.change_format(quantity)
            purchase_price = Kiwoom.change_format(purchase_price)
            current_price = Kiwoom.change_format(current_price)
            eval_profit_loss_price = Kiwoom.change_format(eval_profit_loss_price)
            earning_rate = Kiwoom.change_format2(earning_rate)

            self.opw00018_output['multi'].append([name, quantity, purchase_price, current_price, eval_profit_loss_price,
                                                  earning_rate])

    def _opt10081(self, rqname, trcode):
        data_cnt = self._get_repeat_cnt(trcode, rqname)

        for i in range(data_cnt):
            date = self._get_comm_data(trcode, rqname, i, "일자")
            open = self._get_comm_data(trcode, rqname, i, "시가")
            high = self._get_comm_data(trcode, rqname, i, "고가")
            low = self._get_comm_data(trcode, rqname, i, "저가")
            close = self._get_comm_data(trcode, rqname, i, "현재가")
            volume = self._get_comm_data(trcode, rqname, i, "거래량")

            self.ohlcv['code'].append(self.code)
            self.ohlcv['date'].append(date)
            self.ohlcv['open'].append(int(open))
            self.ohlcv['high'].append(int(high))
            self.ohlcv['low'].append(int(low))
            self.ohlcv['close'].append(int(close))
            self.ohlcv['volume'].append(int(volume))

    @staticmethod
    def change_format(data):
        strip_data = data.lstrip('-0')
        if strip_data == "" or strip_data == ".00":
            strip_data = "0"

        format_data = format(int(strip_data),',d')
        if data.startswith('-'):
            format_data = "-" + format_data

        return format_data

    @staticmethod
    def change_format2(data):
        strip_data = data.lstrip('-0')

        if strip_data == '':
            strip_data = '0'

        if strip_data.startswith('.'):
            strip_data = '0' + strip_data

        if data.startswith('-'):
            strip_data = '-' + strip_data

        return strip_data

    def _opt20006(self, rqname, trcode):

        data_cnt = self._get_repeat_cnt(trcode, rqname)

        for i in range(data_cnt):
            date = self._get_comm_data(trcode, rqname, i, "일자")
            open = self._get_comm_data(trcode, rqname, i, "시가")
            high = self._get_comm_data(trcode, rqname, i, "고가")
            low = self._get_comm_data(trcode, rqname, i, "저가")
            close = self._get_comm_data(trcode, rqname, i, "현재가")
            volume = self._get_comm_data(trcode, rqname, i, "거래량")

            self.ohlcv['code'].append(self.code)
            self.ohlcv['date'].append(date)
            self.ohlcv['open'].append(int(open))
            self.ohlcv['high'].append(int(high))
            self.ohlcv['low'].append(int(low))
            self.ohlcv['close'].append(int(close))
            self.ohlcv['volume'].append(int(volume))

    def dailyCandle(self, code):
        self.ohlcv = {'code': [], 'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}
        self.code = code
        self.cnt = 0
        while self.remained_data == True:
            time.sleep(TR_REQ_TIME_INTERVAL)

            self.set_input_value("종목코드", self.code)
            self.set_input_value("기준일자", "20180131")
            self.set_input_value("수정주가구분", 1)
            if self.cnt > 0:
                next = 2
            else:
                next = 0
            self.comm_rq_data("opt10081_req", "opt10081", next, "0101")
            self.cnt += 1

        return self.ohlcv

if __name__ == "__main__":
    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.comm_connect()

    # kiwoom.reset_opw00018_output()
    # account_no = kiwoom.get_login_info("ACCNO").split(";")[0]
    # kiwoom.set_input_value("계좌번호", account_no)
    # kiwoom.comm_rq_data("opw00018_req", "opw00018", 0, "2000")
    #
    # print(kiwoom.opw00018_output['single'])
    # print(kiwoom.opw00018_output['multi'])
    #

    # kiwoom.set_input_value("계좌번호","8101037411")
    # kiwoom.set_input_value("비밀번호","2248")
    # kiwoom.comm_rq_data("opw00001_req", "opw00001", 0, "2000")
    #
    # print(kiwoom.d2_deposit)

    code = "005930"
    ohlcv = kiwoom.dailyCandle(code)
    print('ok')
