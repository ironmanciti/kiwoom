"""
p.474
"""
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_window()

    def init_window(self):
        self.setGeometry(800, 400, 300, 150)

        groupBox = QGroupBox("시간 선택", self)
        groupBox.resize(100, 100)

        self.radio1 = QRadioButton("일봉", self)
        self.radio1.move(20, 20)
        self.radio2 = QRadioButton("월봉", self)
        self.radio2.move(20, 40)

        self.radio1.clicked.connect(self.radio_button_clicked)
        self.radio2.clicked.connect(self.radio_button_clicked)

        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)

    def radio_button_clicked(self):
        if self.radio1.isChecked():
            msg = "일봉"
        elif self.radio2.isChecked():
            msg = "월봉"   
        else:
            msg = "Invalid 기간"
        self.statusBar.showMessage(msg + " 선택됨")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    sys.exit(app.exec_())

