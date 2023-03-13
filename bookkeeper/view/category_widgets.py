from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QHeaderView, QAbstractItemView

from bookkeeper.models.category import Category
from bookkeeper.view.accessory_widgets import EditButton


class CategoryWidget(QtWidgets.QWidget):
    activate_editing_mode_signal = QtCore.Signal(int)

    def __init__(self) -> None:
        super().__init__()
        self.table = QtWidgets.QTableWidget(20, 4)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel('Категории'))
        layout.addWidget(self.table)

        self.table.setHorizontalHeaderLabels([''] + "ID Родитель Название".split())
        self.table.verticalHeader().hide()
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    def set_data(self, categories: list[Category]) -> None:
        self.table.setRowCount(len(categories))
        for i, cat in enumerate(categories):
            self.table.setCellWidget(i, 0,
                                     EditButton(i, self.activate_editing_mode_signal))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(cat.pk)))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(str(cat.parent)))
            self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(cat.name))

    def set_edit_buttons_active(self, is_active: bool) -> None:
        for i in range(self.table.rowCount()):
            self.table.cellWidget(i, 0).setDisabled(not is_active)


class AddCategoryWidget(QtWidgets.QWidget):
    cancel_signal = QtCore.Signal()
    delete_signal = QtCore.Signal(int)
    update_signal = QtCore.Signal(Category)
    create_signal = QtCore.Signal(Category)

    def __init__(self) -> None:
        super().__init__()
        self.cur_category: Category | None = None
        layout = QtWidgets.QVBoxLayout(self)

        name_layout = QtWidgets.QHBoxLayout()
        parent_layout = QtWidgets.QHBoxLayout()

        label = QtWidgets.QLabel('Родитель')
        label.setFixedWidth(100)
        parent_layout.addWidget(label)
        self.parent_input = QtWidgets.QLineEdit()
        parent_layout.addWidget(self.parent_input)

        label = QtWidgets.QLabel('Название')
        label.setFixedWidth(100)
        name_layout.addWidget(label)
        self.name_input = QtWidgets.QLineEdit()
        name_layout.addWidget(self.name_input)

        layout.addWidget(QtWidgets.QLabel('Добавить новую категорию'))
        layout.addLayout(name_layout)
        layout.addLayout(parent_layout)

        self.add_button = QtWidgets.QPushButton('Добавить')
        self.cancel_button = QtWidgets.QPushButton('Отмена')
        self.delete_button = QtWidgets.QPushButton('Удалить')
        self.update_button = QtWidgets.QPushButton('Сохранить')

        self.add_button.clicked.connect(self.exec_create)
        self.cancel_button.clicked.connect(lambda _: self.cancel_signal.emit())
        self.delete_button.clicked.connect(
            lambda _: self.delete_signal.emit(self.cur_category.pk))
        self.update_button.clicked.connect(self.exec_update)

        self.edit_buttons_layout = QtWidgets.QHBoxLayout()
        self.edit_buttons_layout.addWidget(self.cancel_button)
        self.edit_buttons_layout.addWidget(self.delete_button)
        self.edit_buttons_layout.addWidget(self.update_button)

        self.buttons_placeholder = QtWidgets.QHBoxLayout()
        layout.addLayout(self.buttons_placeholder)
        self.buttons_placeholder.addWidget(self.add_button)

    def exec_create(self) -> None:
        if self.name_input.text() == '' or (
                self.parent_input.text() != '' and
                not self.parent_input.text().isnumeric()):
            return
        parent = None if self.parent_input.text() == '' else int(self.parent_input.text())
        cat = Category(self.name_input.text(), parent)
        self.create_signal.emit(cat)

    def exec_update(self) -> None:
        if self.name_input.text() == '' or (
                self.parent_input.text() != '' and
                not self.parent_input.text().isnumeric()):
            return
        parent = None if self.parent_input.text() == '' else int(self.parent_input.text())
        self.cur_category.parent = parent
        self.cur_category.name = self.name_input.text()
        self.update_signal.emit(self.cur_category)

    def activate_editing_mode(self, category: Category) -> None:
        self.cur_category = category
        self.name_input.setText(category.name)
        parent = str(category.parent) if category.parent is not None else ''
        self.parent_input.setText(parent)
        self.buttons_placeholder.itemAt(0).widget().setParent(None)
        self.buttons_placeholder.addLayout(self.edit_buttons_layout)

    def deactivate_editing_mode(self) -> None:
        self.cur_category = None
        self.buttons_placeholder.itemAt(0).layout().setParent(None)
        self.buttons_placeholder.addWidget(self.add_button)
        self.name_input.clear()
        self.parent_input.clear()
