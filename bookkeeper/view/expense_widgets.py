from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QHeaderView, QAbstractItemView

from bookkeeper.models.expense import Expense
from bookkeeper.view.accessory_widgets import EditButton, DateWidget


class ExpensesWidget(QtWidgets.QWidget):
    activate_editing_mode_signal = QtCore.Signal(int)

    def __init__(self) -> None:
        super().__init__()
        self.expenses: list[Expense] = []
        self.table = QtWidgets.QTableWidget(20, 5)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel('Последние расходы'))
        layout.addWidget(self.table)

        self.table.setHorizontalHeaderLabels(
            [''] + "Дата Сумма Категория Комментарий".split())
        self.table.verticalHeader().hide()
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    def set_data(self, expenses: list[Expense],
                 category_id_name_mapping: dict[int, str]) -> None:
        self.expenses = expenses
        self.table.setRowCount(len(expenses))
        for i, exp in enumerate(expenses):
            self.table.setCellWidget(i, 0,
                                     EditButton(i, self.activate_editing_mode_signal))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(
                str(exp.expense_date.date())))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(str(exp.amount)))
            self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(
                category_id_name_mapping[exp.category]))
            self.table.setItem(i, 4, QtWidgets.QTableWidgetItem(exp.comment))

    def set_edit_buttons_active(self, is_active: bool) -> None:
        for i in range(self.table.rowCount()):
            self.table.cellWidget(i, 0).setDisabled(not is_active)


class AddExpensesWidget(QtWidgets.QWidget):
    cancel_signal = QtCore.Signal()
    delete_signal = QtCore.Signal(int)
    update_signal = QtCore.Signal(Expense, str)
    create_signal = QtCore.Signal(Expense, str)

    def __init__(self) -> None:
        super().__init__()
        self.cur_expense: Expense | None = None
        layout = QtWidgets.QVBoxLayout(self)

        date_layout = QtWidgets.QHBoxLayout()
        sum_layout = QtWidgets.QHBoxLayout()
        cat_layout = QtWidgets.QHBoxLayout()
        comment_layout = QtWidgets.QHBoxLayout()

        label = QtWidgets.QLabel('Дата')
        label.setFixedWidth(100)
        date_layout.addWidget(label)
        self.date_input = DateWidget()
        date_layout.addWidget(self.date_input)

        label = QtWidgets.QLabel('Сумма')
        label.setFixedWidth(100)
        sum_layout.addWidget(label)
        self.sum_input = QtWidgets.QLineEdit()
        sum_layout.addWidget(self.sum_input)

        label = QtWidgets.QLabel('Категория')
        label.setFixedWidth(100)
        cat_layout.addWidget(label)
        self.cat_input = QtWidgets.QComboBox()
        cat_layout.addWidget(self.cat_input)

        label = QtWidgets.QLabel('Комментарий')
        label.setFixedWidth(100)
        comment_layout.addWidget(label)
        self.comment_input = QtWidgets.QLineEdit()
        comment_layout.addWidget(self.comment_input)

        layout.addWidget(QtWidgets.QLabel('Добавить новую запись'))
        layout.addLayout(date_layout)
        layout.addLayout(sum_layout)
        layout.addLayout(cat_layout)
        layout.addLayout(comment_layout)

        self.add_button = QtWidgets.QPushButton('Добавить')
        self.cancel_button = QtWidgets.QPushButton('Отмена')
        self.delete_button = QtWidgets.QPushButton('Удалить')
        self.update_button = QtWidgets.QPushButton('Сохранить')

        self.add_button.clicked.connect(self.exec_create)
        self.cancel_button.clicked.connect(lambda _: self.cancel_signal.emit())
        self.delete_button.clicked.connect(
            lambda _: self.delete_signal.emit(self.cur_expense.pk))
        self.update_button.clicked.connect(self.exec_update)

        self.edit_buttons_layout = QtWidgets.QHBoxLayout()
        self.edit_buttons_layout.addWidget(self.cancel_button)
        self.edit_buttons_layout.addWidget(self.delete_button)
        self.edit_buttons_layout.addWidget(self.update_button)

        self.buttons_placeholder = QtWidgets.QHBoxLayout()
        layout.addLayout(self.buttons_placeholder)
        self.buttons_placeholder.addWidget(self.add_button)

    def exec_create(self) -> None:
        if self.sum_input.text() == '' or not self.sum_input.text().isnumeric():
            return
        exp = Expense(amount=int(self.sum_input.text()),
                      category=0,
                      expense_date=self.date_input.dateTime().toPython(),
                      comment=self.comment_input.text())
        self.create_signal.emit(exp, self.cat_input.currentText())

    def exec_update(self) -> None:
        if self.sum_input.text() == '' or not self.sum_input.text().isnumeric():
            return
        self.cur_expense.amount = int(self.sum_input.text())
        self.cur_expense.comment = self.comment_input.text()
        self.cur_expense.expense_date = self.date_input.dateTime().toPython()
        self.update_signal.emit(self.cur_expense, self.cat_input.currentText())

    def activate_editing_mode(self, expense: Expense, cat_name: str) -> None:
        self.cur_expense = expense
        self.sum_input.setText(str(expense.amount))
        self.cat_input.setCurrentText(cat_name)
        self.comment_input.setText(expense.comment)
        self.date_input.setDate(QtCore.QDate(expense.expense_date.year,
                                             expense.expense_date.month,
                                             expense.expense_date.day))
        self.buttons_placeholder.itemAt(0).widget().setParent(None)
        self.buttons_placeholder.addLayout(self.edit_buttons_layout)

    def deactivate_editing_mode(self) -> None:
        self.cur_expense = None
        self.buttons_placeholder.itemAt(0).layout().setParent(None)
        self.buttons_placeholder.addWidget(self.add_button)

        self.sum_input.clear()
        self.cat_input.setCurrentIndex(0)
        self.comment_input.clear()
        self.date_input.setDate(QtCore.QDate.currentDate())
