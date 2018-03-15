import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5 import uic
from PyQt5.QtCore import *

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from kiwoom import *

form_class = uic.loadUiType("pytrader.ui")[0]

class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.kiwoom = Kiwoom()
        self.kiwoom.comm_connect()

        # 주기적으로 연결상태 아래에 update
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.timeout)

        # 실시간 조회  check 된 경우 주기적 update
        self.timer2 = QTimer(self)
        self.timer2.start(1000*10) # 10 초 주기로 갱신
        self.timer2.timeout.connect(self.timeout2)

        self.code.textChanged.connect(self.code_changed)
        self.cashOrder.clicked.connect(self.send_order)

        self.inquiry.clicked.connect(self.check_balance)

        accounts_num = int(self.kiwoom.get_login_info("ACCOUNT_CNT"))
        accounts = self.kiwoom.get_login_info("ACCNO")
        account_list = accounts.split(';')[0:accounts_num]
        self.account.addItems(account_list)

    def check_balance(self):
        account = self.account.currentText()
        print(account)
        cnt = 0
        self.kiwoom.set_input_value("계좌번호", account)

        self.kiwoom.reset_opw00018_output()
        while self.kiwoom.remained_data:
            time.sleep(0.2)
            if cnt > 0:
                next = 2
            else:
                next = 1
            self.kiwoom.comm_rq_data("opw00018_req", "opw00018", next, "2000")
            cnt += 1

        self.kiwoom.comm_rq_data("opw00001_req", "opw00001", 0, "2000")
        item = QTableWidgetItem(self.kiwoom.d2_deposit)
        item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.tableWidget.setItem(0, 0, item)

        # balance
        n = len(self.kiwoom.opw00018_output['single'])
        if n > 0:
            for i in range(1, 6):
                item = QTableWidgetItem(self.kiwoom.opw00018_output['single'][i-1])
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
                self.tableWidget.setItem(0, i, item)
        self.tableWidget.resizeRowsToContents()

        # Item list
        item_count = len(self.kiwoom.opw00018_output['multi'])
        self.tableWidget_2.setRowCount(item_count)

        for j in range(item_count):
            row = self.kiwoom.opw00018_output['multi'][j]
            for i in range(len(row)):
                item = QTableWidgetItem(row[i])
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
                self.tableWidget_2.setItem(j, i, item)

        self.tableWidget_2.resizeRowsToContents()

    def send_order(self):
        order_type_lookup = {"신규매수": 1, "신규매도": 2, "매수취소": 3, "매도취소": 4}
        hoga_lookup = {"지정가": "00", "시장가": "03"}

        account = self.account.currentText()
        order_type = self.orderType.currentText()
        code = self.code.text()
        hoga = self.hoga.currentText()
        quantity = self.quantity.value()
        price = self.price.value()

        self.kiwoom.send_order("send_order_req", "0101", account, order_type_lookup[order_type],
                    code, quantity, price, hoga_lookup[hoga], "")


    def code_changed(self):
        code = self.code.text()
        name = self.kiwoom.get_master_code_name(code)
        self.codeName.setText(name)

    def timeout(self):
        current_time = QTime.currentTime()
        text_time = current_time.toString("hh:mm:ss")
        time_msg = "현재시간: " + text_time

        state = self.kiwoom.get_connect_state()
        if state == 1:
            state_msg = "서버 연결 중"
        else:
            state_msg = "서버 미연결 중"

        self.statusbar.showMessage(state_msg + " | " + time_msg)

    def timeout2(self):
        if self.checkBox.isChecked():
            self.check_balance()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
