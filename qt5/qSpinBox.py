"""
p.481
"""

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_window()

    def init_window(self):
        self.setGeometry(100, 100, 300, 300)
        self.setWindowTitle("Python")

        label = QLabel("매도수량", self)
        label.move(20, 20)

        self.qSpinBox = QSpinBox(self)
        self.qSpinBox.move(100, 20)
        self.qSpinBox.resize(80, 22)
        self.qSpinBox.setValue(40)
        self.qSpinBox.setSingleStep(10)
        self.qSpinBox.setMinimum(10)
        self.qSpinBox.setMaximum(1000)

        self.qSpinBox.valueChanged.connect(self.spinBoxChanged)

        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)

    def spinBoxChanged(self):
        val = self.qSpinBox.value()
        self.statusBar.showMessage(str(val) + " 주 선택")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    sys.exit(app.exec_())

