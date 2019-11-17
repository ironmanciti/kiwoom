# -*- coding: utf-8 -*-
#직접 수행 혹은  다른 프로그램에서 import kiwoomMain 하여 사용
#from kiwoomMain import *
#dict = kiwoomMain.dailyCandle(code, end_date) - 종목코드, 기준일자
#df = pd.DataFrame.from_dict(dict) - DataFrame 반환

import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import pandas as pd
import logging
from logging.handlers import TimedRotatingFileHandler

TR_REQ_TIME_INTERVAL = 0.2

#-------------------------------------------------------------------------------------------------
# logger 준비하기
#-------------------------------------------------------------------------------------------------
if not os.path.exists('logs'):
    os.makedirs('logs')
# 로그 파일 핸들러
fh_log = TimedRotatingFileHandler('logs/log', when='midnight', encoding='utf-8', backupCount=120)
fh_log.setLevel(logging.DEBUG)

# 콘솔 핸들러
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)

# 로깅 포멧 설정
formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
fh_log.setFormatter(formatter)
sh.setFormatter(formatter)

# 로거 생성
logger = logging.getLogger('kiwoomMain')
logger.setLevel(logging.DEBUG)
logger.addHandler(fh_log)
logger.addHandler(sh)
#-------------------------------------------------------------------------------------------------

class Kiwoom(QAxWidget):

    def __init__(self):
        super().__init__()
        self._create_kiwoom_instance()       # 키움 OpenAPI+ 호출을 위한 COM object 생성
        self._set_signal_slots()             # 키움서버로부터 발생한 이벤트(signal) 을 처리할 method(slot) 연결

    def _create_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1") # kiwoom's ProgID registered in windows registry

    def _set_signal_slots(self):
        self.OnEventConnect.connect(self._event_connect)       # OnEventConnect 이벤트 : _event_connect 호출
        self.OnReceiveTrData.connect(self._receive_tr_data)
        self.OnReceiveChejanData.connect(self._receive_chejan_data)  # 주문체결 시점에 발생 event

    def comm_connect(self): # 1 번 Method
        self.dynamicCall("CommConnect()")      # execute login window
        self.login_event_loop = QEventLoop()   # create event loop instance using QEventLoop class of PyQt
        self.login_event_loop.exec_()          # call exec_ method of the event loop instance
        # 여기서 이벤트 루프를 생성시켰으므로 키움서버로부터 OnEventConnect 이벤트 발생할 때까지 종료되지 않고 대기

    def comm_rq_data(self, sRQName, sTrCode, nPrevNext, sScreenNo):  # 3번 Method : Tran 을 서버로 송신
        self.dynamicCall("CommRqData(QString, QString, int, QString)", sRQName, sTrCode, nPrevNext,sScreenNo)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

    def get_login_info(self, sTag):     # 4번 Method : 계좌정보 및 사용자 정보
        ret = self.dynamicCall("GetLoginInfo(QString)", sTag)
        return ret

    # 5번 Method : 주식 주문
    # sRQName - 사용자구분 요청 명, sScreenNo - 화면번호[4], sAccNo - 계좌번호[10]
    # nOrderType - 주문유형 (1:신규매수, 2:신규매도, 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정)
    # sCode - 주식종목코드, sQty - 주문수량, nPrice - 주문단가, sHogaGb - 거래구분, sOrgOrderNo - 원주문번호
    def send_order(self, sRQName, sScreenNo, sAccNo, nOrderType, sCode, nQty, nPrice, sHogaGb, sOrgOrderNo):
        self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                        [sRQName, sScreenNo, sAccNo, nOrderType, sCode, nQty, nPrice, sHogaGb, sOrgOrderNo])

    def set_input_value(self, sID, sValue):    # 7번 Method
        # sID -아이템명, sValue - 입력값 (ex. ('종목코드','000660'), ('계좌번호','5015123401'))
        self.dynamicCall("SetInputValue(QString, QString)", sID, sValue)

    def _get_repeat_cnt(self, sTrCode, sRecordName):   # 11번 Method : 몇개의 data 가 반환 되었는지 갯수 알아내는 API
        # sTrCode - Tran 명, sRecordName - 레코드명
        ret = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRecordName)
        return ret                    # 레코드의 반복 횟수

    def get_code_list_by_market(self, sMarket):  # 14번 Method : 시장구분에 따른 종목코드 반환
        # smarket : 시장코드 0:장내, 3:ELW, 8: ETF, 10:코스닥
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", sMarket)
        code_list = code_list.split(';')        # ;로 구분된 6자리종목코드를 list 변환 ex. 900090;900080;900130;)
        return code_list[:-1]                   # 종목코드를 python list 로 반환

    def get_connect_state(self):              # 15번 Method : 현재의 접속 상태
        ret = self.dynamicCall("GetConnectState()")    # 0: 미연결, 1: 연결완료
        return ret

    def get_master_code_name(self, sTrCode):  # 16번 Method : 종목코드 한글명 반환
        code_name = self.dynamicCall("GetMasterCodeName(QString)", sTrCode)  # code: 종목코드
        return code_name                      # 종목한글명

    def _get_comm_data(self, strTrCode, strRecordName, nIndex, strItemName):  # 24번 Method : 수신데이터를 반환
        # strTrCode - TR 명, strRecordName - 레코드명, nIndex - TR 반복부, strItemName - TR 에서 얻어올 출력항목명
        ret = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                strTrCode, strRecordName, nIndex, strItemName)
        return ret.strip()

    def get_chejan_data(self, nFid):           # 26번 Method : 체결잔고 data get
        ret = self.dynamicCall("GetChejanData(int)", nFid)    # nFid - 체결잔고 아이템 (10 - 현재가출력)
        return ret

    def get_future_list(self):                 # 29번 Method : 지수선물 리스트 반환
        future_list = self.dynamicCall("GetFutureList()")
        future_list = future_list.split(';')        # ;로 구분된 8자리종목코드를 list 변환 ex. 101J9000;101JC000;)
        return future_list[:-1]                     # 종목코드를 python list 로 반환

    def get_future_code_by_index(self, nIndex):     # 30번 Method : 지수선물 코드 반환 ex) 0: 최근월선물, 4: 최근월스프레드
        future_code = self.dynamicCall("GetFutureCodeByIndex(int)", nIndex)
        return future_code

    def get_act_price_list(self):                   # 31번 Method : 지수옵션 행사가 리스트 반환
        price_list = self.dynamicCall("GetActPriceList()")
        price_list = price_list.split(';')          # ;로 구분된 행사가를 list 변환 ex. 265.00;252.20;260.00;)
        return price_list[:-1]

    def get_month_list(self):                       # 32번 Method : 지수옵션 월물 리스트 반환
        month_list = self.dynamicCall("GetMonthList()")
        month_list = month_list.split(';')          # 201412;201409;201408;201407;...
        return month_list[:-1]

    def get_option_code(self, strActPrice, nCp, strMonth):     # 33번 Method : 행사가, 콜풋, 월물로 종목코드를 구함
        # strActPrice: 행사가(소숫점포함) nCp: 2- 콜, 3- 풋, strMonth: 월물(6자리) (ex. "260.00", 2, "201407")
        code = self.dynamicCall("GetOptionCode(QString,int,QString)", strActPrice, nCp, strMonth)
        return code                           # 종목코드

    # 34번 Method : 입력된 종목코드와 동일한 행사가의 코드 중 입력한 월물의 코드를 구함
    def get_option_code_by_month(self, strCode, nCp, strMonth):
        # strCode: 종목코드 nCp: 2- 콜, 3- 풋, strMonth: 월물(6자리) (ex. "201J7260", 2, "201407")
        code = self.dynamicCall("GetOptionCodeByMonth(QString,int,QString)", strCode, nCp, strMonth)
        return code                           # 종목코드

    def get_option_atm(self):                       # 44번 Method : 지수옵션 ATM 반환
        atm = self.dynamicCall("GetOptionATM()")
        return atm

    def get_server_gubun(self):               # KOA_Functions
        ret = self.dynamicCall("KOA_Functions(QString, QString)", "GetServerGubun", "")
        return ret

    def _event_connect(self, err_code):        # OnEventConnect 이벤트 발생하면 호출된다.
        if err_code == 0:
            logger.debug("login success")                 # 연결성공
        elif err_code == 100:
            logger.debug("사용자 정보교환실패")
        elif err_code == 101:
            logger.debug("서버접속 실패")
        elif err_code == 102:
            logger.debug("버전처리 실패")
        else:
            print("connection failed, error code = {}".format(err_code))

        self.login_event_loop.exit()           # comm_connect 호출시 생성되었던 event loop 종료

    def _receive_chejan_data(self, gubun, item_cnt, fid_list):
        print(gubun)
        print(self.get_chejan_data(9203)) # 주문번호
        print(self.get_chejan_data(302))  # 종목명
        print(self.get_chejan_data(900))  # 주문수량
        print(self.get_chejan_data(901))  # 주문가격
        print(self.get_chejan_data(902))  # 미체결수량
        print(self.get_chejan_data(910))  # 체결가
        print(self.get_chejan_data(911))  # 체결량

    def _receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, ununsed2, unused3, unused4):
        if next == '2':
            self.remained_data = True   # 서버에 호출할 데이터가 더 남아 있음
        else:
            self.remained_data = False

        if rqname == "opt10001_req":    #주식기본정보요청
            self._opt10001(rqname, trcode)

        if rqname == "opt10002_req":    #주식거래원요청
            self._opt10002(rqname, trcode)

        if rqname == "opt10060_req":    #종목별투자자기관별차트요청
            self._opt10060(rqname, trcode)

        if rqname == "opt10081_req":    #주식일봉차트요청(종목코드/기준일자/수정주가구분 "1":유상증자)
            self._opt10081(rqname, trcode)

        if rqname == "opt10085_req":    #계좌수익률요청
            self._opt10085(rqname, trcode)

        if rqname == "opt10086_req":    #일별주가요청
            self._opt10086(rqname, trcode)

        if rqname == "opt20001_req":    #업종현재가요청(시장구분/업종코드)
            self._opt10081(rqname, trcode)  # opt10081 과 처리 logic 공유

        if rqname == "opt20006_req":    #업종일봉조회요청(업종코드/기준일자)
            self._opt20006(rqname, trcode)

        if rqname == "opw00001_req":    #예수금상세현황요청
            self._opw00001(rqname, trcode)

        if rqname == "opw00018_req":    #계좌평가잔고내역요청
            self._opw00018(rqname, trcode)

        try:
            self.tr_event_loop.exit()   # OnReceiveTrData 이벤트를 받았으므로 이벤트 루프 대기상태 종료
        except AttributeError:
            pass

    def _opt10001(self, rqname, trcode):    # 주식기본정보요청(single data)
        self.code_name = self._get_comm_data(trcode, rqname, 0, "종목명")
        self.closing_month = self._get_comm_data(trcode, rqname, 0, "결산월")
        self.par_value = self._get_comm_data(trcode, rqname, 0, "액면가")
        self.per = self._get_comm_data(trcode, rqname, 0, "PER")
        self.highest_250 = self._get_comm_data(trcode, rqname, 0, "250최고")
        self.lowest_250  = self._get_comm_data(trcode, rqname, 0, "250최저")
        self.current_price = self._get_comm_data(trcode, rqname, 0, "시가")

    def reset_opt10002_output(self):        # 주식거래원요청 (multi data)
        self.opt10002_output = []

    def _opt10002(self, rqname, trcode):    # 주식거래원요청 (multi data)
        data_cnt = self._get_repeat_cnt(trcode, rqname)  # 반환된 data 갯수
        for i in range(data_cnt):
            updown = self._get_comm_data(trcode, rqname, i, "등락율")
            seller_name1 = self._get_comm_data(trcode, rqname, i, "매도거래원명1")
            sell_volume1 = self._get_comm_data(trcode, rqname, i, "매도거래량1")
            self.opt10002_output.append([updown, seller_name1, sell_volume1])

    def reset_opt10060_output(self):        # 종목별투자자기관별차트요청 (multi data)
        self.opt10060_output = []

    def _opt10060(self, rqname, trcode):    # 종목별투자자기관별차트요청 (multi data)
        data_cnt = self._get_repeat_cnt(trcode, rqname)  # 반환된 data 갯수

        for i in range(data_cnt):
            date = self._get_comm_data(trcode, rqname, i, "일자")
            person = self._get_comm_data(trcode, rqname, i, "개인투자자")
            foreigner = self._get_comm_data(trcode, rqname, i, "외국인투자자")
            institute = self._get_comm_data(trcode, rqname, i, "기관계")
            financial_invest = self._get_comm_data(trcode, rqname, i, "금융투자")
            self.opt10060_output.append([date, person, foreigner, institute, financial_invest])

    def _opt10081(self, rqname, trcode):                 # 주식일봉차트조회(multi-data)요청
        data_cnt = self._get_repeat_cnt(trcode, rqname)  # 반환된 data 갯수

        for i in range(data_cnt):
            date = self._get_comm_data(trcode, rqname, i, "일자")
            open = self._get_comm_data(trcode, rqname, i, "시가")
            high = self._get_comm_data(trcode, rqname, i, "고가")
            low = self._get_comm_data(trcode, rqname, i, "저가")
            close = self._get_comm_data(trcode, rqname, i, "현재가")
            volume = self._get_comm_data(trcode, rqname, i, "거래량")

            # kiwoom instance 생성한 program 에서 kiwoom.ohlcv dictionary 생성
            self.ohlcv['code'].append(self.code)
            self.ohlcv['date'].append(date)
            self.ohlcv['open'].append(int(open))
            self.ohlcv['high'].append(int(high))
            self.ohlcv['low'].append(int(low))
            self.ohlcv['close'].append(int(close))
            self.ohlcv['volume'].append(int(volume))

    def reset_opt10085_output(self):                 # 계좌수익률요청(multi-data)
        self.opt10085_output = []

    def _opt10085(self, rqname, trcode):                 # 계좌수익률요청(multi-data)
        data_cnt = self._get_repeat_cnt(trcode, rqname)  # 반환된 data 갯수

        for i in range(data_cnt):
            date = self._get_comm_data(trcode, rqname, i, "일자")
            code = self._get_comm_data(trcode, rqname, i, "종목코드")
            code_name = self._get_comm_data(trcode, rqname, i, "종목명")
            current_price = self._get_comm_data(trcode, rqname, i, "현재가")
            purchase_price = self._get_comm_data(trcode, rqname, i, "매입가")
            purchase_amount = self._get_comm_data(trcode, rqname, i, "매입금액")
            stock_volume = self._get_comm_data(trcode, rqname, i, "보유수량")
            self.opt10085_output.append([date, code, code_name, current_price, purchase_price, purchase_amount,
                            stock_volume])

    def _opt10086(self, rqname, trcode):                 # 일별주가요청(multi-data)
        data_cnt = self._get_repeat_cnt(trcode, rqname)  # 반환된 data 갯수

        for i in range(data_cnt):
            date = self._get_comm_data(trcode, rqname, i, "날짜")
            open = self._get_comm_data(trcode, rqname, i, "시가")
            high = self._get_comm_data(trcode, rqname, i, "고가")
            low = self._get_comm_data(trcode, rqname, i, "저가")
            close = self._get_comm_data(trcode, rqname, i, "종가")
            volume = self._get_comm_data(trcode, rqname, i, "거래량")
            credit_ratio = self._get_comm_data(trcode, rqname, i, "신용비")
            foreigner_net_buy = self._get_comm_data(trcode, rqname, i, "외인순매수")
            inst_net_buy = self._get_comm_data(trcode, rqname, i, "기관순매수")
            # kiwoom instance 생성한 program 에서 kiwoom.dailyprice dictionary 생성
            self.dailyprice['code'].append(self.code)
            self.dailyprice['date'].append(date)
            self.dailyprice['open'].append(int(open))
            self.dailyprice['high'].append(int(high))
            self.dailyprice['low'].append(int(low))
            self.dailyprice['close'].append(int(close))
            self.dailyprice['volume'].append(int(volume))
            self.dailyprice['credit_ratio'].append(float(credit_ratio))
            # -- 하락 & minus, +- 상승 & minus
            foreigner_net_buy = Kiwoom.remove_first_minus(foreigner_net_buy)
            self.dailyprice['foreigner_net_buy'].append(int(foreigner_net_buy))
            inst_net_buy = Kiwoom.remove_first_minus(inst_net_buy)
            self.dailyprice['inst_net_buy'].append(int(inst_net_buy))

    def _opt20006(self, rqname, trcode):           # 업종일봉조회(multi data)요청
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
            self.ohlcv['open'].append(float(open))
            self.ohlcv['high'].append(float(high))
            self.ohlcv['low'].append(float(low))
            self.ohlcv['close'].append(float(close))
            self.ohlcv['volume'].append(int(volume))

    def _opw00001(self, rqname, trcode):    #예수금상세현황요청
        order_allowable_amt = self._get_comm_data(trcode, rqname, 0, "주문가능금액")
        d2_deposit = self._get_comm_data(trcode, rqname, 0, "d+2추정예수금")
        self.order_allowable_amt = Kiwoom.change_format(order_allowable_amt)
        self.d2_deposit = Kiwoom.change_format(d2_deposit)

    def reset_opw00018_output(self):        #계좌평가잔고내역요청
        self.opw00018_output = {'single': [], 'multi': []}

    def _opw00018(self, rqname, trcode):    #계좌평가잔고내역요청
        # single data
        total_purchase_price = self._get_comm_data(trcode, rqname, 0, "총매입금액")
        total_eval_price = self._get_comm_data(trcode, rqname, 0, "총평가금액")
        total_eval_profit_loss_price = self._get_comm_data(trcode, rqname, 0, "총평가손익금액")
        total_earning_rate = self._get_comm_data(trcode, rqname, 0, "총수익률(%)")
        estimated_deposit = self._get_comm_data(trcode, rqname, 0, "추정예탁자산")

        self.opw00018_output['single'].append(Kiwoom.change_format(total_purchase_price))
        self.opw00018_output['single'].append(Kiwoom.change_format(total_eval_price))
        self.opw00018_output['single'].append(Kiwoom.change_format(total_eval_profit_loss_price))

        total_earning_rate = str(total_earning_rate)

        if self.get_server_gubun():                               # 1: 모의투자서버, 나머지: 실서버
            total_earning_rate = float(total_earning_rate) / 100  # 모의투자는 소숫점 2자리 포함한 퍼센트
            total_earning_rate = str(total_earning_rate)          # 실서버는 소숫점 없이 수익률 전달

        self.opw00018_output['single'].append(total_earning_rate)

        self.opw00018_output['single'].append(Kiwoom.change_format(estimated_deposit))

        # multi data
        rows = self._get_repeat_cnt(trcode, rqname)
        for i in range(rows):
            name = self._get_comm_data(trcode, rqname, i, "종목명")
            quantity = self._get_comm_data(trcode, rqname, i, "보유수량")
            purchase_price = self._get_comm_data(trcode, rqname, i, "매입가")
            current_price = self._get_comm_data(trcode, rqname, i, "현재가")
            eval_profit_loss_price = self._get_comm_data(trcode, rqname, i, "평가손익")
            earning_rate = self._get_comm_data(trcode, rqname, i, "수익률(%)")

            quantity = Kiwoom.change_format(quantity)
            purchase_price = Kiwoom.change_format(purchase_price)
            current_price = Kiwoom.change_format(current_price)
            eval_profit_loss_price = Kiwoom.change_format(eval_profit_loss_price)
            earning_rate = Kiwoom.change_format2(earning_rate)

            self.opw00018_output['multi'].append([name, quantity, purchase_price, current_price, eval_profit_loss_price,
                                                  earning_rate])

    @staticmethod
    def change_format(data):
        strip_data = data.lstrip('-0')                 # 문자열 왼쪽의 -, 0 문자열 제거
        if strip_data == "" or strip_data == ".00":
            strip_data = "0"

        format_data = format(int(strip_data),',d')      # 천단위마다 , 추가
        if data.startswith('-'):                        # data 가 - 로 시작하면 - 추가
            format_data = "-" + format_data

        return format_data

    @staticmethod
    def change_format2(data):
        strip_data = data.lstrip('-0')              # 문자열 왼쪽의 -, 0 문자열 제거

        if strip_data == '':
            strip_data = '0'

        if strip_data.startswith('.'):              # 소숫점 있으면 0. 으로 변환
            strip_data = '0' + strip_data

        if data.startswith('-'):
            strip_data = '-' + strip_data           # -로 시작하면 - 추가

        return strip_data

    @staticmethod
    def remove_first_minus(data):

        if data.startswith('--'):
            data = data[1:]           # --로 시작하면 - 추가
        if data == '':
            data = 0
        return data

def kw_get_future_list():
    future_list = kiwoom.get_future_list()   # 지수선물 리스트
    for i in range(len(future_list)):
        logger.debug(future_list[i])

def kw_get_future_code_by_index(code):
    # 지수선물 코드 반환 ex) 0: 최근월선물, 1: 차근월물, 2: 차차근월물, 3: 차차차근월물, 4: 최근월스프레드
    future_code = kiwoom.get_future_code_by_index(code)
    logger.debug(future_code)       # ex) 101NC000 - K200선물1812, 101P3000 - K200선물1903

def kw_get_act_price_list():   # 지수옵션 행사가 리스트
    price_list = kiwoom.get_act_price_list()
    for i in range(len(price_list)):
        logger.debug(price_list[i])

def kw_get_month_list():      # 지수옵션 월물 리스트
    month_list = kiwoom.get_month_list()
    for i in range(len(month_list)):
        logger.debug(month_list[i])

def kw_get_option_code(act_price, cp, month):    # 행사가, 콜풋구분, 월물로 종목코드 구하기
    code = kiwoom.get_option_code(act_price, cp, month)
    logger.debug(code)     #201NA300

def kw_get_option_code_by_month(code, cp, month):  # 종목코드와 동일한 행사가의 다른 월물 코드
     other_code = kiwoom.get_option_code_by_month(code, cp, month)
     logger.debug(other_code)

def kw_get_option_atm():         # 지수옵션 ATM
    logger.debug(kiwoom.get_option_atm())

def kw_get_opt10001(code):       # 주식기본정보요청
    kiwoom.set_input_value("종목코드",code)
    kiwoom.comm_rq_data("opt10001_req", "opt10001", 0, "0101")

    logger.debug(kiwoom.closing_month)
    logger.debug(kiwoom.par_value)
    logger.debug(kiwoom.per)
    logger.debug(kiwoom.highest_250)
    logger.debug(kiwoom.lowest_250)
    logger.debug(kiwoom.current_price)

def kw_get_opt10002(code):      # 주식거래원요청
    kiwoom.reset_opt10002_output()
    kiwoom.set_input_value("종목코드",code)
    kiwoom.comm_rq_data("opt10002_req", "opt10002", 0, "0101")
    for i in range(len(kiwoom.opt10002_output)):
        for j in range(3):
            logger.debug(kiwoom.opt10002_output[i][j])

def kw_get_opw00018():          # 계좌평가잔고내역요청
    kiwoom.reset_opw00018_output()
    account_no = kiwoom.get_login_info("ACCNO").split(";")[0]
    kiwoom.set_input_value("계좌번호", account_no)
    kiwoom.comm_rq_data("opw00018_req", "opw00018", 0, "0101") # RQName, trcode, 0:조회/2:연속, 화면번호

    logger.debug(account_no)
    logger.debug(kiwoom.opw00018_output['single'])
    logger.debug(kiwoom.opw00018_output['multi'])

def kw_get_opt10085():          # 계좌수익률요청
    kiwoom.reset_opt10085_output()
    kiwoom.set_input_value("계좌번호","8108830011")
    kiwoom.comm_rq_data("opt10085_req", "opt10085", 0, "0101")
    label = ["일자","종목코드","종목명","현재가","매입가","매입금액","보유수량"]
    for i in range(len(kiwoom.opt10085_output)):
        for j in range(7):
            logger.debug(label[j] + kiwoom.opt10085_output[i][j])
        logger.debug(" ")

def kw_get_opw00001(account_no):    # 예수금상세현황요청
    kiwoom.set_input_value("계좌번호",account_no)
    # kiwoom.set_input_value("비밀번호","2248")   # 계좌비밀번호 저장으로 아이콘 설정하면 필요 없음
    kiwoom.comm_rq_data("opw00001_req", "opw00001", 0, "0101")
    logger.debug("주문가능금액 :" + kiwoom.order_allowable_amt)
    logger.debug("d+2추정예수금 :" + kiwoom.d2_deposit)

if __name__ == "__main__":

    app = QApplication(sys.argv)    # QAxWidget class 가 정상 작동하려면 QApplication instance 필요
    kiwoom = Kiwoom()               # kiwoom 객체 생성
    kiwoom.comm_connect()           # login 수행

    # kw_get_future_list()   # 지수선물 리스트
    # kw_get_future_code_by_index(1)  # 지수선물 코드 반환
    # kw_get_act_price_list()   # 지수옵션 행사가 리스트
    # kw_get_month_list()         # 지수옵션 월물 리스트
    # kw_get_option_code("300.00", 2, "201810")
    # kw_get_option_code("292.50", 3, "201810")
    # kw_get_option_code_by_month("201NA300", 3, "201811")  # 종목코드와 동일한 행사가의 다른 월물 코드
    # kw_get_option_atm()      # 지수옵션 ATM
    # kw_get_opt10001("000660")    # 주식기본정보요청
    # kw_get_opt10002("000660")    # 주식거래원요청
    # kw_get_opw00018()            # 계좌평가잔고내역요청
    # kw_get_opt10085()             # 계좌수익률요청
    # kw_get_opw00001("8108830011")   # 모의위탁계좌
    # kw_get_opw00001("8741085731")   # 모의 선물옵션계좌
