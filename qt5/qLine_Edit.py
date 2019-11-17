"""
P.472
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
        label = QLabel('종목코드', self)
        label.move(20, 20)

        self.lineEdit = QLineEdit("초기값", self)
        self.lineEdit.move(100, 20)
        self.lineEdit.textChanged.connect(self.lineEditChanged)
        self.lineEdit.returnPressed.connect(self.lineEditChanged)

    def lineEditChanged(self):
        self.statusBar().showMessage(self.lineEdit.text())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    sys.exit(app.exec_())


