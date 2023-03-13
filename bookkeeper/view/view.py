import sys
from typing import Callable
from PySide6 import QtWidgets

from bookkeeper.models.budget import Budget
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.view.abstract_view import AbstractView
from bookkeeper.view.main_window import MainWindow


class View(AbstractView):
    def __init__(self) -> None:
        self.app = QtWidgets.QApplication(sys.argv)
        self.window = MainWindow()

    def run(self) -> None:
        self.window.show()
        sys.exit(self.app.exec())

    def set_category_list(self, categories: list[Category]) -> None:
        self.window.set_category_list(categories)

    def set_budget_list(self, budgets: list[Budget]) -> None:
        self.window.set_budget_list(budgets)

    def set_expense_list(self, expenses: list[Expense]) -> None:
        self.window.set_expense_list(expenses)

    def register_category_creator(self, handler: Callable[[Category], int]) -> None:
        self.window.category_creator = handler

    def register_category_updater(self, handler: Callable[[Category], None]) -> None:
        self.window.category_updater = handler

    def register_category_deleter(self, handler: Callable[[int], None]) -> None:
        self.window.category_deleter = handler

    def register_budget_creator(self, handler: Callable[[Budget], int]) -> None:
        self.window.budget_creator = handler

    def register_budget_updater(self, handler: Callable[[Budget], None]) -> None:
        self.window.budget_updater = handler

    def register_budget_deleter(self, handler: Callable[[int], None]) -> None:
        self.window.budget_deleter = handler

    def register_expense_creator(self, handler: Callable[[Expense], int]) -> None:
        self.window.expense_creator = handler

    def register_expense_updater(self, handler: Callable[[Expense], None]) -> None:
        self.window.expense_updater = handler

    def register_expense_deleter(self, handler: Callable[[int], None]) -> None:
        self.window.expense_deleter = handler
