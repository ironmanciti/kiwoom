import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QAxContainer import *

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.dynamicCall("CommConnect()")

        self.setWindowTitle("PyStock")
        self.setGeometry(300, 300, 500, 450)

        self.kiwoom.OnEventConnect.connect(self.event_connect)
        self.kiwoom.OnReceiveTrData.connect(self.receive_trdata)

        label = QLabel("종목코드 :", self)
        label.move(20, 60)

        self.code_edit = QLineEdit(self)
        self.code_edit.move(100, 60)
        self.code_edit.setText("039490")

        btn1 = QPushButton("조회", self)
        btn1.move(250, 60)
        btn1.clicked.connect(self.btn1_clicked)

        self.text_edit = QTextEdit(self)
        self.text_edit.setGeometry(20, 160, 200, 200)
        self.text_edit.setEnabled(False)

        self.text_edit2 = QTextEdit(self)
        self.text_edit2.setGeometry(250, 160, 100, 100)
        self.text_edit2.setEnabled(False)

    def receive_trdata(self, screen_no, rqname, trcode, recordname, prev_next, dummy1,dummy2, dummy3, dummy4):
        if rqname == 'opt10001_req':
            name = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, 0, "종목명")
            volume = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, 0, "거래량")
            self.text_edit.append("종목명: " + name.strip())
            self.text_edit.append("거래량: " + volume.strip())

    def btn1_clicked(self):
        code = self.code_edit.text()
        self.text_edit.append('종목코드: ' + code)

        self.kiwoom.dynamicCall('SetInputValue(QString, QString)', '종목코드', code)
        self.kiwoom.dynamicCall('CommRqData(QString, QString, int, QString)', 'opt10001_req', 'opt10001', 0, '0101')

    def event_connect(self, err_code):
        if err_code == 0:
            self.statusBar().showMessage("Login 성공")
            accounts = self.kiwoom.dynamicCall("GetLoginInfo(QString)", "ACCNO")
            accounts = accounts.rstrip(';').split(';')
            self.text_edit2.append("구좌번호: ")
            for accnt in accounts:
                self.text_edit2.append(accnt)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
    