import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5 import uic
from PyQt5.QtCore import *

sys.path.append('../lib/')

from kiwoomMain import *

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

        accounts_num = int(self.kiwoom.get_login_info("ACCOUNT_CNT"))  # 계좌정보
        accounts = self.kiwoom.get_login_info("ACCNO")

        account_list = accounts.split(';')[0:accounts_num]
        self.account.addItems(account_list)

        self.code.textChanged.connect(self.code_changed)  # 종목코드 입력
        self.cashOrder.clicked.connect(self.cash_order)   # 현금주문 button click

        self.inquiry.clicked.connect(self.check_balance)  # 잔고및 보유종목 현황

        self.batchOrder.clicked.connect(self.batch_order)  # 일괄 주문

        self.load_buy_sell_list()

    def check_balance(self):
        self.kiwoom.reset_opw00018_output()
        account_number = self.kiwoom.get_login_info("ACCNO")
        account_number = account_number.split(';')[0]

        self.kiwoom.set_input_value("계좌번호", account_number)
        self.kiwoom.comm_rq_data("opw00018_req", "opw00018", 0, "2000")

        while self.kiwoom.remained_data:
            time.sleep(0.2)
            self.kiwoom.set_input_value("계좌번호", account_number)
            self.kiwoom.comm_rq_data("opw00018_req", "opw00018", 2, "2000")

        # opw00001
        self.kiwoom.set_input_value("계좌번호", account_number)
        self.kiwoom.comm_rq_data("opw00001_req", "opw00001", 0, "2000")

        # balance
        item = QTableWidgetItem(self.kiwoom.d2_deposit)
        item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.tableWidget.setItem(0, 0, item)

        for i in range(1, 6):
            item = QTableWidgetItem(self.kiwoom.opw00018_output['single'][i - 1])
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

    def cash_order(self):
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

    def batch_order(self):
        hoga_lookup = {"지정가": "00", "시장가": "03"}

        self.read_buy_sell_list()

        account = self.account.currentText()

        # buy_list batch order
        for row in self.buy_list:
            split_row_data = row.split(';')
            code = split_row_data[1]
            hoga = split_row_data[2]
            quantity = split_row_data[3]
            price = split_row_data[4]

            if split_row_data[-1] == '매수전':
                self.kiwoom.send_order("send_order_req", "0101", account, 2, code, quantity, price,
                                                        hoga_lookup[hoga], "")

        # sell_list batch order
        for row in self.sell_list:
            split_row_data = row.split(';')
            code = split_row_data[1]
            hoga = split_row_data[2]
            quantity = split_row_data[3]
            price = split_row_data[4]

            if split_row_data[-1] == '매도전':
                self.kiwoom.send_order("send_order_req", "0101", account, 1, code, quantity, price,
                                                        hoga_lookup[hoga], "")
        # buy list 주문완료 표시
        for i, row in enumerate(self.buy_list):
            self.buy_list[i] = self.buy_list[i].replace('매수전', '주문완료')

        # sell list 주문완료 표시
        for i, row in enumerate(self.sell_list):
            self.sell_list[i] = self.sell_list[i].replace('매도전', '주문완료')

        self.update_buy_sell_list()
        self.load_buy_sell_list()

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

    def read_buy_sell_list(self):
        f = open("buy_list.txt", "rt")
        self.buy_list = f.readlines()
        f.close()

        f = open("sell_list.txt", "rt")
        self.sell_list = f.readlines()
        f.close()

    def update_buy_sell_list(self):
        f = open("buy_list.txt", "wt")
        for row in self.buy_list:
            f.write(row)
        f.close()

        f = open("sell_list.txt", "wt")
        for row in self.sell_list:
            f.write(row)
        f.close()

    def load_buy_sell_list(self):

        self.read_buy_sell_list()

        row_count = len(self.buy_list) + len(self.sell_list)
        self.tableWidget_3.setRowCount(row_count)

        #buy list
        for j in range(len(self.buy_list)):
            row_data = self.buy_list[j]
            split_row_data = row_data.split(';')
            split_row_data[1] = self.kiwoom.get_master_code_name(split_row_data[1])

            for i in range(len(split_row_data)):
                item = QTableWidgetItem(split_row_data[i])
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
                self.tableWidget_3.setItem(j, i, item)

        #sell list
        for j in range(len(self.sell_list)):
            row_data = self.sell_list[j]
            split_row_data = row_data.split(';')
            split_row_data[1] = self.kiwoom.get_master_code_name(split_row_data[1])

            for i in range(len(split_row_data)):
                item = QTableWidgetItem(split_row_data[i])
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
                self.tableWidget_3.setItem(len(self.buy_list) + j, i, item)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
