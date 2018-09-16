import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *

form_class1 = uic.loadUiType("my_window.ui")[0]
form_class2 = uic.loadUiType("my_dialog.ui")[0]

class LogInDialog(QDialog, form_class2):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.id = None
        self.password = None
        self.setWindowTitle("Sign In")
        self.setWindowIcon(QIcon("icon.png"))

        self.pushButton.clicked.connect(self.pushButtonClicked)

    def pushButtonClicked(self):
        self.id = self.lineEdit_ID.text()
        self.password = self.lineEdit_password.text()
        self.close()

class MyWindow(QWidget, form_class1):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowTitle("Window and Dialog")
        self.setWindowIcon(QIcon("icon.png"))

        self.pushButton.clicked.connect(self.pushButtonClicked)

    def pushButtonClicked(self):
        dlg = LogInDialog()
        dlg.exec_()
        id = dlg.id
        password = dlg.password

        self.label.setText("id: {} password: {}".format(id, password))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec()