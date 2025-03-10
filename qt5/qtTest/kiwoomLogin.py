"""
p.304 기초 API 익히기
"""
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QAxContainer import *

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyStock")
        self.setGeometry(300, 300, 500, 650)

        # 키움 로그인
        self.kiwoom = QAxWidget("KHOPENAPI.KHOPenAPICtrl.1")

        self.btn1 = QPushButton("Login", self)
        self.btn1.move(20, 20)
        self.btn1.clicked.connect(self.btn1_clicked)

        # self.btn2 = QPushButton("조회", self)
        # self.btn2.move(200, 60)
        # self.btn2.clicked.connect(self.btn2_clicked)

        self.text_edit = QTextEdit(self)
        self.text_edit.setGeometry(10, 200, 300, 200)
        self.text_edit.setEnabled(False)

    def btn1_clicked(self):
        ret = self.kiwoom.dynamicCall("CommConnect()")
        # OpenAPI+ Event
        self.kiwoom.OnEventConnect.connect(self.event_connect)
        #self.kiwoom.OnReceiveTrData.connect(self.receive_trdata)

    def event_connect(self, err_code):
        if err_code == 0:
            self.text_edit.append("로그인 성공")

        """
        self.label = QLabel('종목코드', self)
        self.label.move(20, 60)
        self.code_edit = QLineEdit(self)
        self.code_edit.move(100, 60)
        self.code_edit.setText("039490")
    """
       

    """
        self.btn3 = QPushButton("Check status", self)
        self.btn3.move(20, 100)
        self.btn3.clicked.connect(self.btn3_clicked)

        self.btn4 = QPushButton("계좌정보", self)
        self.btn4.move(20, 160)
        self.btn4.clicked.connect(self.btn4_clicked)

        self.btn5 = QPushButton("KOSPI 종목", self)
        self.btn5.move(200, 160)
        self.btn5.clicked.connect(self.btn5_clicked)

        self.btn6 = QPushButton("KOSDAQ 종목", self)
        self.btn6.move(350, 160)
        self.btn6.clicked.connect(self.btn6_clicked)
        
        self.listWidget = QListWidget(self)
        self.listWidget.setGeometry(10, 450, 200, 150)

    def btn2_clicked(self):
        code = self.code_edit.text()
        self.text_edit.append("종목코드 : " + code)

        #SetInputValue
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)

        #CommRqData
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)",
                            "opt10001_req", "opt10001", 0, "0101")

    def btn3_clicked(self):
        if self.kiwoom.dynamicCall("GetConnectState()") == 1:
            self.statusBar().showMessage("Connected")
        else:
            self.statusBar().showMessage("Not connected")

    def btn4_clicked(self):
        account_num = self.kiwoom.dynamicCall("GetLoginInfo(QString)", ["ACCNO"])
        account_cnt = self.kiwoom.dynamicCall("GetLoginInfo(QString)", ["ACCOUNT_CNT"])
        user_id = self.kiwoom.dynamicCall("GetLoginInfo(QString)", ["USER_ID"])
        user_name = self.kiwoom.dynamicCall("GetLoginInfo(QString)", ["USER_NAME"])

        if account_cnt >= "1":
            cnt = int(account_cnt)
            account_num = account_num.split(';')
        else:
            cnt = 0

        for i in range(cnt):
            self.text_edit.append("계좌번호: " + account_num[i].rstrip(';'))

        self.text_edit.append("계좌갯수: " + account_cnt)
        self.text_edit.append("user_id: " + user_id)
        self.text_edit.append("user_name: " + user_name)

    def btn5_clicked(self):
        ret = self.kiwoom.dynamicCall("GetCodeListByMarket(QString)", ["0"])
        kospi_code_list = ret.split(';')
        kospi_code_name_list = []

        for x in kospi_code_list:
            name = self.kiwoom.dynamicCall("GetMasterCodeName(QString)", [x])
            kospi_code_name_list.append(x + ' : ' + name)

        self.listWidget.clear()
        self.listWidget.addItems(kospi_code_name_list)

    def btn6_clicked(self):
        ret = self.kiwoom.dynamicCall("GetCodeListByMarket(QString)", ["10"])
        kospi_code_list = ret.split(';')
        kospi_code_name_list = []

        for x in kospi_code_list:
            name = self.kiwoom.dynamicCall("GetMasterCodeName(QString)", [x])
            kospi_code_name_list.append(x + ' : ' + name)

        self.listWidget.clear()
        self.listWidget.addItems(kospi_code_name_list)
    
    def receive_trdata(self, screen_no, rqname, trcode, recordname, prev_next, data_len,
                             err_code, msg1, msg2):
        if rqname == "opt10001_req":
            name = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)",
                                                        trcode, rqname, 0, "종목명")
            volume = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)",
                                                        trcode, rqname, 0, "거래량")
            self.text_edit.append("종목명: " + name.strip())
            self.text_edit.append("거래량: " + volume.strip())
"""
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywindow = MyWindow()
    mywindow.show()
    app.exec_()
