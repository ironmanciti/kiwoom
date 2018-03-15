import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *

form_class = uic.loadUiType("basicWidgets.ui")[0]

class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        #----------- QPushButton
        self.clickButton.clicked.connect(self.clickBtn_clicked)
        self.clearButton.clicked.connect(self.clearBtn_clicked)
        self.closeButton.clicked.connect(QCoreApplication.instance().quit)

        #----------- QLineEdit
        self.code.textChanged.connect(self.code_changed) # 한글자씩 입력때마다 statusBar display
        # self.code.returnPressed.connect(self.code_changed) # 전체 입력하고 return 누르면 statusBar display
        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)

        #----------- QRadioButton
        self.radio1.setChecked(True)
        self.statusBar.showMessage("일봉 선택 됨")
        self.radio1.clicked.connect(self.radioButtonClicked)
        self.radio2.clicked.connect(self.radioButtonClicked)
        self.radio3.clicked.connect(self.radioButtonClicked)

        #----------- QCheckBox
        self.checkBox1.stateChanged.connect(self.checkBoxStatus)
        self.checkBox2.stateChanged.connect(self.checkBoxStatus)
        self.checkBox3.stateChanged.connect(self.checkBoxStatus)

        #------------ QSpinBox
        self.spinBox.setValue(10)
        self.spinBox.setSingleStep(10)
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(1000)
        self.spinBox.valueChanged.connect(self.spinBoxChanged)

    def clickBtn_clicked(self):
        self.message.setText("버튼이 click 되었습니다.")

    def clearBtn_clicked(self):
        self.message.clear()

    def code_changed(self):
        self.statusBar.showMessage(self.code.text())

    def radioButtonClicked(self):
        msg = ""
        if self.radio1.isChecked():
            msg = "일봉"
        elif self.radio2.isChecked():
            msg = "주봉"
        else:
            msg = "월봉"
        self.statusBar.showMessage(msg + " 선택 됨")

    def checkBoxStatus(self):
        msg = "이동평균:"
        if self.checkBox1.isChecked():
            msg += " 5 일"
        if self.checkBox2.isChecked():
            msg += " 20 일"
        if self.checkBox3.isChecked():
            msg += " 60 일"
        if self.checkBox1.isChecked() != True and \
           self.checkBox2.isChecked() != True and \
           self.checkBox3.isChecked() != True:
           msg = ""
        self.statusBar.showMessage(msg + " 선택 됨")

    def spinBoxChanged(self):
        val = self.spinBox.value()
        msg = "%d 주를 매도합니다." % (val)
        self.statusBar.showMessage(msg)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
