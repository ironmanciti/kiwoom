import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QAxContainer import *

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        #Kiwoom Login
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.dynamicCall("CommConnect()")

        #OpenAPI + Event
        #self.kiwoom.OnEventConnect.connect(self.event_connect)

        self.setWindowTitle('종목코드')
        self.setGeometry(300, 300, 300, 150)

        btn1 = QPushButton("종목코드 얻기", self)
        btn1.move(190,20)
        btn1.clicked.connect(self.btn1_clicked)

        self.listWidget= QListWidget(self)
        self.listWidget.setGeometry(10,10,170,130)

    def btn1_clicked(self):
        ret = self.kiwoom.dynamicCall("GetCodeListByMarket(QString)", ["0"])
        kospi_code_list = ret.split(';')
        kospi_code_name_list = []

        for n in kospi_code_list:
            name = self.kiwoom.dynamicCall("GetMasterCodeName(QString)", [n])
            kospi_code_name_list.append(n + " : " + name)

        print("total no = " + str(len(kospi_code_list)))
        self.listWidget.addItems(kospi_code_name_list)

    # def event_connect(self, err_code):
    #     if err_code == 0:
    #         self.text_edit.append("successfully logged in...")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
