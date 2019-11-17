import sys
from PyQt5.QtWidgets import *

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.setGeometry(800, 200, 500, 500)
        self.checkbox1 = QCheckBox("상한가")
        self.checkbox2 = QCheckBox("하한가")
        self.checkbox3 = QCheckBox("시가총액상위")
        self.checkbox4 = QCheckBox("시가총액하위")
        
        leftInner = QVBoxLayout()

        group = QGroupBox("검색옵션")
        leftInner.addWidget(self.checkbox1)
        leftInner.addWidget(self.checkbox2)
        leftInner.addWidget(self.checkbox3)
        leftInner.addWidget(self.checkbox4)
        group.setLayout(leftInner)

        leftLayout = QVBoxLayout()
        leftLayout.addWidget(group)

        table = QTableWidget(10, 5)
        table.setHorizontalHeaderLabels(["종목코드", "종목명", "현재가", "등락률", "거래량"])

        rightInner = QVBoxLayout()
        rightInner.addWidget(table)

        outerLayout = QHBoxLayout()

        outerLayout.addLayout(leftLayout)
        outerLayout.addLayout(rightInner)

        self.setLayout(outerLayout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywindow = MyWindow()
    mywindow.show()
    app.exec_()
