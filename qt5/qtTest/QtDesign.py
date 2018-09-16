import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *

form_class = uic.loadUiType("main_window.ui")[0]

kospi_top5 = {
        'code': ['005930', '015760','005380','090430', '012330'],
        'name': ['삼성전자', '한국전력', '현대차', '아모레퍼시픽', '현대모비스'],
        'cprice': ['45,000', '60,100', '132,000', '414,500', '243,500']
}
column_idx_lookup = {'code': 0, 'name': 1, 'cprice': 2}

class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()

        self.setupUi(self)

        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)

        self.pushButton1.clicked.connect(self.btn1_clicked)
        self.pushButton2.clicked.connect(self.btn2_clicked)

        self.lineEdit.textChanged.connect(self.lineEditChanged)

        self.radio_day.setChecked(True)
        self.statusBar.showMessage("일봉 선택 됨")

        self.radio_day.clicked.connect(self.radioButtonClicked)
        self.radio_week.clicked.connect(self.radioButtonClicked)
        self.radio_month.clicked.connect(self.radioButtonClicked)

        self.checkBox1.stateChanged.connect(self.checkBoxState)
        self.checkBox2.stateChanged.connect(self.checkBoxState)
        self.checkBox3.stateChanged.connect(self.checkBoxState)

        self.spinBox.setValue(10)
        self.spinBox.setSingleStep(10)
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(10000)
        self.spinBox.valueChanged.connect(self.spinBoxChanged)

        self.tableWidget.setRowCount(5)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.setTableWidgetData()

    def setTableWidgetData(self):
        column_headers = ['종목코드', '종목명', '종가']
        self.tableWidget.setHorizontalHeaderLabels(column_headers)

        for k, v in kospi_top5.items():
            col = column_idx_lookup[k]
            for row, val in enumerate(v):
                item = QTableWidgetItem(val)
                if col == 2:
                    item.setTextAlignment(Qt.AlignRight)
                self.tableWidget.setItem(row, col, item)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

    def spinBoxChanged(self):
        value = self.spinBox.value()
        msg = "{} 주를 팝니다.".format(value)
        self.statusBar.showMessage(msg)

    def checkBoxState(self):
        msg = ""
        if self.checkBox1.isChecked():
            msg += '5일'
        if self.checkBox2.isChecked():
            msg += '20일'
        if self.checkBox3.isChecked():
            msg += '60일'
        self.statusBar.showMessage(msg)

    def radioButtonClicked(self):
        msg = ""
        if self.radio_day.isChecked():
            msg = "일봉"
        elif self.radio_week.isChecked():
            msg = "주봉"
        else:
            msg = "월봉"
        self.statusBar.showMessage(msg + "선택 됨")

    def btn1_clicked(self):
        self.label.setText("버튼이 클릭되었습니다.")

    def btn2_clicked(self):
        self.label.clear()

    def lineEditChanged(self):
        self.statusBar.showMessage(self.lineEdit.text())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()

