import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_window()

    def init_window(self):
        self.setGeometry(300, 300, 400, 400)
        self.setWindowTitle("Main Window")

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('QLineEdit 사용예')
    
        qlineEditButton = QAction(QIcon('poly.png'), 'QLineEdit', self)
        qlineEditButton.triggered.connect(self.qLine_Edit)

        fileMenu.addAction(qlineEditButton)

    def qLine_Edit(self):
        label = QLabel("종목코드", self)
        self.lineEdit = QLineEdit("", self)
        self.lineEdit.move(80, 30)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    sys.exit(app.exec_())