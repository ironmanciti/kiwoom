import sys 
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from dialog_login import *

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.setGeometry(1100, 200, 300, 100)
        self.setWindowTitle("Login Main")
        self.setWindowIcon(QIcon('icons82.png'))

        self.pushButton = QPushButton("Sign In")
        self.pushButton.clicked.connect(self.pushButtonClicked)
        self.label = QLabel()

        layout = QVBoxLayout()
        layout.addWidget(self.pushButton)
        layout.addWidget(self.label)

        self.setLayout(layout)

    def pushButtonClicked(self):
        dlg = LogInDialog()
        dlg.exec_()
        id = dlg.id 
        pswd = dlg.pswd
        self.label.setText("id: {}, password: {}".format(id, pswd))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow() 
    window.show() 
    app.exec_()
