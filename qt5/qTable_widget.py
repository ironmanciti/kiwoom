"""
p.484
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

        self.table = QTableWidget(self)
        self.table.resize(290, 290)
        self.table.setRowCount(5)
        self.table.setColumnCount(3)
        self.setTableData()

    def setTableData(self):
        top_500 = {
            'code': ['005930', '015760', '005380', '090430', '012330'],
            'name': ['삼성전자', '한국전력', '현대차', '아모레퍼시픽', '현대모비스'],
            'cprice': ['45,000', '60,100', '132,000', '414,500', '243,500']
        }
        col_idx_lookup = {'code': 0, 'name':1, 'cprice': 2}

        self.table.setHorizontalHeaderLabels(["종목코드", "종목명", "주가"]) 

        for k, v in top_500.items():
            col = col_idx_lookup[k]
            print(k, v, col)
            for row, val in enumerate(v):
                item = QTableWidgetItem(val)
                self.table.setItem(row, col, item)
                if col == 2:
                    item.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
            self.table.resizeColumnsToContents()
            self.table.resizeRowsToContents()       

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    sys.exit(app.exec_())

