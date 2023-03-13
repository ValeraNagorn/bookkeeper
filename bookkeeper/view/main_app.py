"""
Main файл приложения
"""

import os

from bookkeeper.models.budget import Budget
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.repository.abstract_repository import AbstractRepository
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.utils import read_tree, INIT_CATEGORIES, DB_NAME
from bookkeeper.view.abstract_view import AbstractView
from bookkeeper.view.view import View


class Bookkeeper:
    """
    Presenter с графическим интерфейсом
    """
    def __init__(self, view: AbstractView,
                 category_repo: AbstractRepository[Category],
                 expense_repo: AbstractRepository[Expense],
                 budget_repo: AbstractRepository[Budget]) -> None:
        self.view = view
        self.category_repo = category_repo
        self.expense_repo = expense_repo
        self.budget_repo = budget_repo

        self.view.register_expense_updater(self.update_expense)
        self.view.register_expense_deleter(self.delete_expense)
        self.view.register_expense_creator(self.create_expense)

        self.view.register_category_updater(self.update_category)
        self.view.register_category_deleter(self.delete_category)
        self.view.register_category_creator(self.create_category)

        self.view.register_budget_updater(self.budget_repo.update)
        self.view.register_budget_creator(self.budget_repo.add)

    def init_db(self) -> None:
        """
        default db objects insertion
        """
        Category.create_from_tree(read_tree(INIT_CATEGORIES), self.category_repo)
        self.expense_repo.add(Expense(120, 1, comment='comment1'))
        self.expense_repo.add(Expense(900, 7, comment='comment2'))
        # bud_repo.add(Budget(1, None, 1000))
        self.budget_repo.add(Budget(7, None, 7000))
        self.budget_repo.add(Budget(30, None, 30000))

    def run(self) -> None:
        self.view.set_category_list(self.category_repo.get_all())
        self.view.set_expense_list(self.expense_repo.get_all())
        self.view.set_budget_list(self.budget_repo.get_all())
        self.view.run()

    def update_expense(self, expense: Expense) -> None:
        self.expense_repo.update(expense)
        self.view.set_expense_list(self.expense_repo.get_all())

    def delete_expense(self, pk: int) -> None:
        self.expense_repo.delete(pk)
        self.view.set_expense_list(self.expense_repo.get_all())

    def create_expense(self, expense: Expense) -> int:
        pk = self.expense_repo.add(expense)
        self.view.set_expense_list(self.expense_repo.get_all())
        return pk

    def update_category(self, category: Category) -> None:
        self.category_repo.update(category)
        self.view.set_category_list(self.category_repo.get_all())

    def delete_category(self, pk: int) -> None:
        self.category_repo.delete(pk)
        self.view.set_category_list(self.category_repo.get_all())

    def create_category(self, category: Category) -> int:
        pk = self.category_repo.add(category)
        self.view.set_category_list(self.category_repo.get_all())
        return pk


db_init_needed = not os.path.isfile(DB_NAME)

app_view: AbstractView = View()
cat_repo = SQLiteRepository[Category](DB_NAME, Category)
exp_repo = SQLiteRepository[Expense](DB_NAME, Expense)
bud_repo = SQLiteRepository[Budget](DB_NAME, Budget)

bk = Bookkeeper(app_view, cat_repo, exp_repo, bud_repo)
if db_init_needed:
    bk.init_db()

bk.run()
