import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import pandas as pd

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        self._create_kiwoom_instance()
        self._set_signal_slots()

    def _create_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")  #--> kiwoom's ProgID registered in windows registry

    def _set_signal_slots(self):
        self.OnEventConnect.connect(self._event_connect)

    def comm_connect(self):
        self.dynamicCall("CommConnect()")   # --> execute login window
        self.login_event_loop = QEventLoop()  #--> create instance using QEventLoop class of PyQt
        self.login_event_loop.exec_()  # --> call exec_ method of the instance

    def _event_connect(self, err_code):
        if err_code == 0:
            print("connected")
        else:
            print("disconnected")

        self.login_event_loop.exit()

    def get_code_list_by_market(self, market):
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market) # call Kiwoom method
        code_list = code_list.split(';')
        return code_list[:-1]

    def get_master_code_name(self, code):
        code_name = self.dynamicCall("GetMasterCodeName(QString)", code)
        return code_name

def dbUpdate(codeDict, smarket):
    import sqlite3
    con = sqlite3.connect("D:\SQLITEDB\koreaStock.db")
    cursor = con.cursor()

    df = pd.DataFrame(codeDict, columns=['code','code_name','smarket'])
    df.to_sql('stockCode', con, if_exists='replace')

    con.commit()
    con.close()
    print('complete')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    markets = ['0', '3', '8', '10']   # 0: KOSPI, 3: ELW, 10: KOSDAQ, 8:ETF
    kiwoom = Kiwoom()
    kiwoom.comm_connect()

    code_list = {}

    for smarket in markets:
        list = kiwoom.get_code_list_by_market(smarket)
        code_list[smarket] = list

    codeDict = {'code': [], 'code_name': [], 'smarket': []}

    for smarket, list in code_list.items():
        for code in list:
            code_name = kiwoom.get_master_code_name(code)
            codeDict['code'].append(code)
            codeDict['code_name'].append(code_name)
            codeDict['smarket'].append(smarket)

    dbUpdate(codeDict, smarket)

    #for code in code_list:
        #print(code, end=" ")
