import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from iexfinance import get_historical_data 
from datetime import datetime
import pandas as pd
from pandas import Series, DataFrame

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):

        self.setGeometry(600, 200, 1200, 600)
        self.setWindowTitle("PyChart Viewer v0.1")
        self.setWindowIcon(QIcon("icon.png"))

        self.lineEdit = QLineEdit()
        self.pushButton = QPushButton("차트그리기")
        self.pushButton.clicked.connect(self.pushButtonClicked)

        self.fig = plt.figure()
        self.canvas = FigureCanvas(self.fig)

        leftLayout = QVBoxLayout()
        leftLayout.addWidget(self.canvas)

        rightLayout = QVBoxLayout()
        rightLayout.addWidget(self.lineEdit)
        rightLayout.addWidget(self.pushButton)
        rightLayout.addStretch(1)

        layout = QHBoxLayout()
        layout.addLayout(leftLayout)
        layout.addLayout(rightLayout)
        layout.setStretchFactor(leftLayout, 1)
        layout.setStretchFactor(rightLayout, 0)

        self.setLayout(layout)


    def pushButtonClicked(self):
        code = self.lineEdit.text()
        
        start = datetime(2017, 1, 1) # starting date: year-month-date
        end = datetime(2018, 5, 13) # ending date: year-month-date

        df = get_historical_data(code, start=start, end=end, output_format='pandas') 
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['MA60'] = df['close'].rolling(window=60).mean()
        
        ax = self.fig.add_subplot(111)
        ax.plot(df.index, df['close'], label='Close')
        ax.plot(df.index, df['MA20'], label='MA20')
        ax.plot(df.index, df['MA60'], label='MA60')
        ax.legend(loc='upper right')
        ax.grid()
        
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()