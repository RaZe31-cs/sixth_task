import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QApplication, QTableWidgetItem, QMainWindow

from UI.AddEdit import Ui_MainWindow
from UI.mainui import Ui_Form

DATABASE = 'data/coffee.sqlite'


class AddEditDatabase(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUi()

    def initUi(self):
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(['ID', 'название сорт', 'степень обжарки', 'молотый/в зернах',
                                              'описание вкуса', 'цена', 'объем упаковки'])
        self.con = sqlite3.connect(DATABASE)
        self.cur = self.con.cursor()
        res = self.cur.execute('SELECT * FROM coffee_info').fetchall()
        self.table.setRowCount(len(res))
        # print(res)
        for i, info in enumerate(res):
            for j in range(7):
                self.table.setItem(i, j, QTableWidgetItem(str(info[j])))
        self.table.cellClicked.connect(self.push_table)
        self.pushButton.clicked.connect(self.push_table)

    def push_table(self, *args):
        self.AddEdit = AddEditSmallForm(args, self)
        self.AddEdit.show()


class AddEditSmallForm(QMainWindow, Ui_MainWindow):
    def __init__(self, args, parent):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        self.args = args
        self.pushButton_2.clicked.connect(self.close_Form)
        self.pushButton.clicked.connect(self.AddEdit)
        self.initUi()

    def initUi(self):
        self.table_column = ('name_of_sort', 'degree_of_roasting',
                             'ground_or_in_grains', 'info_taste', 'price', 'volume')

        self.comboBox.addItems(['Легкая', 'Средняя', 'Темная'])
        self.comboBox_2.addItems(('Молотый', 'Зерна'))
        if self.args[0] is False:
            pass
        else:
            self.lineEdit.setText(self.parent.table.item(self.args[0], 1).text())

            self.comboBox.setCurrentText(self.parent.table.item(self.args[0], 2).text())

            self.comboBox_2.setCurrentText(self.parent.table.item(self.args[0], 3).text())

            self.plainTextEdit.setPlainText(self.parent.table.item(self.args[0], 4).text())

            self.spinBox.setValue(int(self.parent.table.item(self.args[0], 5).text()))

            self.doubleSpinBox.setValue(float(self.parent.table.item(self.args[0], 6).text()))

    def close_Form(self):
        self.close()

    def AddEdit(self):
        if self.check_confirm_form():
            if self.args[0] is False:
                self.parent.cur.execute('''INSERT INTO coffee_info(name_of_sort, degree_of_roasting,
                 ground_or_in_grains, info_taste, price, volume) VALUES(?, ?, ?, ?, ?, ?)''',
                                        (self.lineEdit.text().strip(),
                                         self.comboBox.currentText().strip(),
                                         self.comboBox_2.currentText().strip(),
                                         self.plainTextEdit.toPlainText().strip(),
                                         int(self.spinBox.value()),
                                         float(self.doubleSpinBox.value())))
                self.parent.con.commit()
                self.statusBar().showMessage('Информация успешно загружена')
            else:
                self.res = self.parent.cur.execute("""SELECT * FROM coffee_info WHERE id = (?)""",
                                                   (int(self.parent.table.item(self.args[0], 0).text()),)).fetchall()
                item = (self.lineEdit.text().strip(),
                        self.comboBox.currentText().strip(),
                        self.comboBox_2.currentText().strip(),
                        self.plainTextEdit.toPlainText().strip(),
                        int(self.spinBox.value()),
                        float(self.doubleSpinBox.value()))
                for i, info in enumerate(self.res[0][1:]):
                    if info != item[i]:
                        self.parent.cur.execute(
                            f"""UPDATE coffee_info SET 
                            {self.table_column[i]} = '{item[i]}' 
                            WHERE id = {self.res[0][0]}""")
                self.parent.con.commit()
            self.parent.initUi()
            QTimer.singleShot(600, lambda: self.close())

    def check_confirm_form(self) -> bool:
        if (self.lineEdit.text().strip() != '' and
                self.spinBox.value() != 0 and
                float(self.doubleSpinBox.value()) != 0.0):
            return True
        else:
            self.statusBar().showMessage('Форма заполнена неверно')
            QTimer.singleShot(5000, lambda: self.statusBar().showMessage(''))
            return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AddEditDatabase()
    ex.show()
    sys.exit(app.exec())
