from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QHeaderView

from bookkeeper.models.budget import Budget


class DateWidget(QtWidgets.QDateEdit):
    def __init__(self, date: QtCore.QDate = QtCore.QDate.currentDate()) -> None:
        super().__init__(date)
        self.setCalendarPopup(True)
        self.setDisplayFormat('dd.MM.yyyy')
        calendar = self.calendarWidget()
        calendar.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
        calendar.setGridVisible(True)


class EditButton(QtWidgets.QPushButton):
    edit_icon = None

    @classmethod
    def get_icon(cls) -> QtGui.QPixmap:
        if not cls.edit_icon:
            cls.edit_icon = QtGui.QPixmap('view/edit.png')
        return cls.edit_icon

    def __init__(self, index: int, on_click_signal: QtCore.SignalInstance) -> None:
        super().__init__(self.get_icon(), '')
        self.index = index
        self.on_click_signal = on_click_signal
        self.setIconSize(QSize(25, 25))
        self.clicked.connect(lambda _: self.on_click_signal.emit(self.index))


class BudgetWidget(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.table = QtWidgets.QTableWidget(3, 2)
        self.budgets: list[Budget] = []

        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                           QtWidgets.QSizePolicy.Policy.Maximum)
        self.setFixedHeight(156)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel('Бюджет'))
        layout.addWidget(self.table)

        self.table.setHorizontalHeaderLabels("Сумма Бюджет".split())
        self.table.setVerticalHeaderLabels("День Неделя Месяц".split())
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.set_expenses([0, 0, 0])

        self.table.item(0, 0).setFlags(
            self.table.item(0, 0).flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
        self.table.item(1, 0).setFlags(
            self.table.item(1, 0).flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
        self.table.item(2, 0).setFlags(
            self.table.item(2, 0).flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)

    def set_budgets(self, budgets: list[Budget]) -> None:
        self.budgets = budgets[:3]
        for_day = budgets[0]
        for_week = budgets[1]
        for_month = budgets[2]
        self.table.setItem(0, 1, QtWidgets.QTableWidgetItem(
            str(for_day.amount) if for_day else ''))
        self.table.setItem(1, 1, QtWidgets.QTableWidgetItem(
            str(for_week.amount) if for_week else ''))
        self.table.setItem(2, 1, QtWidgets.QTableWidgetItem(
            str(for_month.amount) if for_month else ''))

    def set_expenses(self, expenses: list[int]) -> None:
        for_day, for_week, for_month = expenses[:3]
        self.table.setItem(0, 0, QtWidgets.QTableWidgetItem(str(for_day)))
        self.table.setItem(1, 0, QtWidgets.QTableWidgetItem(str(for_week)))
        self.table.setItem(2, 0, QtWidgets.QTableWidgetItem(str(for_month)))
