"""
p.478
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

       self.checkbox1 = QCheckBox("5일 이동평균선", self)
       self.checkbox2 = QCheckBox("20일 이동평균선", self)
       self.checkbox3 = QCheckBox("60일 이동평균선", self)

       self.checkbox1.resize(150, 30)
       self.checkbox2.resize(150, 30)
       self.checkbox3.resize(150, 30)
       self.checkbox1.move(20, 20)
       self.checkbox2.move(20, 40)
       self.checkbox3.move(20, 60)

       self.checkbox1.stateChanged.connect(self.checkBoxState)
       self.checkbox2.stateChanged.connect(self.checkBoxState)
       self.checkbox3.stateChanged.connect(self.checkBoxState)
       self.statusBar = QStatusBar(self)
       self.setStatusBar(self.statusBar)

    def checkBoxState(self):
        msg = ""
        if self.checkbox1.isChecked():
            msg += "5일"
        if self.checkbox2.isChecked():
            msg += "20일"
        if self.checkbox3.isChecked():
            msg += "60일"
        
        self.statusBar.showMessage(msg + " selected")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    sys.exit(app.exec_())

