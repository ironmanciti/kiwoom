import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *

form_class = uic.loadUiType("QWidget.ui")[0]

class MyWindow(QWidget, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.pushButton.clicked.connect(self.pushButtonClicked)

        self.pushButton_2.clicked.connect(self.pushButton_2_clicked)

    def pushButtonClicked(self):
        fname = QFileDialog.getOpenFileName(self)
        self.label.setText(fname[0])

    def pushButton_2_clicked(self):
        text, ok = QInputDialog.getInt(self, "매수 수량", "매수 수량을 입력하세요")
        msg = ""
        if ok:
            msg += str(text)
            self.label.setText(msg)

        items = ("KOSPI", "KOSDAQ", "KONEX")
        item, ok = QInputDialog.getItem(self, "시장선택", "시장을 선택하세요", items, 0, False)
        if ok and item:
            msg += item
            self.label.setText(msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec()