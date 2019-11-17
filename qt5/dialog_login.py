"""
p.501
"""
import sys 
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class LogInDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setupUI()

        self.id = None
        self.pswd = None 

    def setupUI(self):
        self.setGeometry(1100, 200, 300, 100)
        self.setWindowTitle("Sign In")
        self.setWindowIcon(QIcon('icons8.png'))

        label1 = QLabel("ID:")
        label2 = QLabel("Password:")

        self.lineEdit1 = QLineEdit()
        self.lineEdit2 = QLineEdit()
        self.pushButton1 = QPushButton("Sign In")
        self.pushButton1.clicked.connect(self.pushButtonClicked)

        layout = QGridLayout()
        layout.addWidget(label1, 0, 0)
        layout.addWidget(label2, 1, 0)
        layout.addWidget(self.lineEdit1, 0, 1)
        layout.addWidget(self.lineEdit2, 1, 1)
        layout.addWidget(self.pushButton1,0, 2)

        self.setLayout(layout)

    def pushButtonClicked(self):
        self.id = self.lineEdit1.text()
        self.pswd = self.lineEdit2.text()
        self.close()
