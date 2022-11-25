import sqlite3 as sql
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem


class Espresso(QMainWindow):
    def __init__(self, db_name, headers):
        super(Espresso, self).__init__()
        uic.loadUi("UI.ui", self)
        self.headers = headers
        self.initDB(db_name)
        self.initUI()
        self.refresh_table()

    def initDB(self, db_name):
        self.db = sql.connect(db_name)
        self.cur = self.db.cursor()

    def initUI(self):
        self.pushButton.clicked.connect(self.refresh_table)

    def refresh_table(self):
        table = self.cur.execute("SELECT * FROM coffee").fetchall()
        self.tableWidget.setHorizontalHeaderLabels(self.headers)
        if len(table) == 0:
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(0)
            return
        self.tableWidget.setRowCount(len(table))
        self.tableWidget.setColumnCount(len(self.headers))
        for i, row in enumerate(table):
            for j, elem in enumerate(row):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))
        self.tableWidget.resizeColumnsToContents()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    wid = Espresso("coffee.sqlite", ["ID", "Название сорта", "Степень обжарки", "Молотый/в зёрнах", "Описание вкуса",
                                     "Цена", "Объём упаковки"])
    wid.show()
    sys.exit(app.exec())
