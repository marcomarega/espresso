import sqlite3 as sql
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from UI import Ui_MainWindow
from addEditCoffeeForm import Ui_MainWindow as AddEditUI

from PyQt5 import QtCore, QtWidgets

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class Espresso(QMainWindow, Ui_MainWindow):
    def __init__(self, db_name, headers):
        super(Espresso, self).__init__()
        self.setupUi(self)
        self.headers = headers
        self.initDB(db_name)
        self.initUI()
        self.refresh_table()

    def initDB(self, db_name):
        self.db = sql.connect(db_name)
        self.cur = self.db.cursor()

    def initUI(self):
        self.pushButton.clicked.connect(self.refresh_table)
        self.add_action.triggered.connect(self.add_coffee)
        self.edit_action.triggered.connect(self.edit_coffee)

    def add_coffee(self):
        self.add_coffee_window = AddEditCoffeeWindow(self, self.db, self.cur)
        self.add_coffee_window.show()

    def edit_coffee(self):
        selected_items = self.tableWidget.selectedItems()
        if len(selected_items) == 0:
            return
        selected_id = self.tableWidget.item(selected_items[0].row(), 0).text()
        self.edit_coffee_window = AddEditCoffeeWindow(self, self.db, self.cur, id=selected_id)
        self.edit_coffee_window.show()

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


class AddEditCoffeeWindow(QMainWindow, AddEditUI):
    def __init__(self, parent, db, cur, id=None):
        super(AddEditCoffeeWindow, self).__init__()
        self.setupUi(self)
        self.parent_window = parent
        self.db = db
        self.cur = cur
        self.id = id
        self.initUI()

    def initUI(self):
        self.button.clicked.connect(self.statusbar.clearMessage)
        self.button.clicked.connect(self.add_edit_data)
        if self.id is not None:
            initial_form = self.cur.execute("SELECT * FROM coffee WHERE ID = ?", (int(self.id),)).fetchone()
            self.title_edit.setText(str(initial_form[1]))
            self.roast_edit.setText(str(initial_form[2]))
            self.beans_edit.setText(str(initial_form[3]))
            self.taste_edit.setText(str(initial_form[4]))
            self.cost_edit.setText(str(initial_form[5]))
            self.volume_edit.setText(str(initial_form[6]))

    def add_edit_data(self):
        title, roast, beans, taste, cost, volume = self.title_edit.text().strip(), self.roast_edit.text().strip(), \
                                                  self.beans_edit.text().strip(), self.taste_edit.text().strip(), \
                                                  self.cost_edit.text().strip(), self.volume_edit.text().strip()
        if (len(title) == 0 or len(roast) == 0 or len(beans) == 0 or
                len(taste) == 0 or len(cost) == 0 or len(volume) == 0):
            self.statusbar.showMessage("Пустые поля недопустимы")
            return
        try:
            cost = int(cost)
            volume = int(volume)
        except Exception:
            self.statusbar.showMessage("Некорректно заполнены поля")
            return
        if self.id is None:
            self.cur.execute("INSERT INTO coffee(title, roast, beans, taste, cost, volume)"
                             "VALUES(?, ?, ?, ?, ?, ?)", (title, roast, beans, taste, cost, volume))
            self.db.commit()
        else:
            self.cur.execute("UPDATE coffee SET title = ?, roast = ?, beans = ?, taste = ?, cost = ?, volume = ? "
                             "WHERE id = ?", (title, roast, beans, taste, cost, volume, int(self.id)))
            self.db.commit()
        self.parent_window.refresh_table()
        self.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    wid = Espresso("coffee.sqlite", ["ID", "Название сорта", "Степень обжарки", "Молотый/в зёрнах", "Описание вкуса",
                                     "Цена", "Объём упаковки"])
    wid.show()
    sys.exit(app.exec())
