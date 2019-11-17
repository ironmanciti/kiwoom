"""
p.509
"""
import sys 
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import matplotlib.pyplot as plt 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import yfinance as yf
import pandas as pd
import datetime 

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(600, 200, 1200, 600)
        self.setWindowTitle("Pychart Viewer")
        self.setWindowIcon(QIcon('icons8.png'))

        self.lineEdit = QLineEdit()
        self.pushButton = QPushButton("차트그리기")
        self.pushButton.clicked.connect(self.pushButtonClicked)

        self.fig = plt.figure() 
        self.canvas = FigureCanvas(self.fig)

        leftlayout = QVBoxLayout()
        leftlayout.addWidget(self.canvas)

        rightlayout = QVBoxLayout()
        rightlayout.addWidget(self.lineEdit)
        rightlayout.addWidget(self.pushButton)
        rightlayout.addStretch(1)

        layout = QHBoxLayout()
        layout.addLayout(leftlayout)
        layout.addLayout(rightlayout)
        layout.setStretchFactor(leftlayout, 1)
        layout.setStretchFactor(rightlayout, 0)

        self.setLayout(layout)

    def pushButtonClicked(self):

        ticker = self.lineEdit.text()
        start = datetime.datetime(2019,1,1)
        df = yf.Ticker(ticker).history(start=start)
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA60'] = df['Close'].rolling(window=60).mean()

        ax = self.fig.add_subplot(111)
        ax.plot(df.index, df['Close'], label='Close')
        ax.plot(df.index, df['MA20'], label='MA20')
        ax.plot(df.index, df['MA60'], label='MA60')
        ax.legend(loc='best')
        ax.grid()

        self.canvas.draw()
        ax.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    windows = MyWindow()
    windows.show()
    app.exec_()

