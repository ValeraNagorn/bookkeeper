from typing import Protocol, Callable

from bookkeeper.models.budget import Budget
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense


class AbstractView(Protocol):
    def run(self) -> None:
        pass

    def set_category_list(self, categories: list[Category]) -> None:
        pass

    def set_budget_list(self, categories: list[Budget]) -> None:
        pass

    def set_expense_list(self, categories: list[Expense]) -> None:
        pass

    def register_category_creator(self, handler: Callable[[Category], int]) -> None:
        pass

    def register_category_updater(self, handler: Callable[[Category], None]) -> None:
        pass

    def register_category_deleter(self, handler: Callable[[int], None]) -> None:
        pass

    def register_budget_creator(self, handler: Callable[[Budget], int]) -> None:
        pass

    def register_budget_updater(self, handler: Callable[[Budget], None]) -> None:
        pass

    def register_budget_deleter(self, handler: Callable[[int], None]) -> None:
        pass

    def register_expense_creator(self, handler: Callable[[Expense], int]) -> None:
        pass

    def register_expense_updater(self, handler: Callable[[Expense], None]) -> None:
        pass

    def register_expense_deleter(self, handler: Callable[[int], None]) -> None:
        pass
