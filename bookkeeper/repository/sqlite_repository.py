"""
Модуль описывает репозиторий, работающий с SQLite3
"""

import sqlite3
from datetime import datetime
from inspect import get_annotations
from sqlite3 import Connection
from types import UnionType
from typing import Any, get_args

from bookkeeper.repository.abstract_repository import AbstractRepository, T


class SQLiteRepository(AbstractRepository[T]):
    """
    Репозиторий, работающий с SQLite3. Хранит данные в базе данных.
    """

    def __init__(self, db_file: str, cls: type) -> None:
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop('pk')
        self.cls = cls

        definition_strings = [
            f'{f_name} {self.__class__._resolve_type(f_type)}'
            for f_name, f_type in self.fields.items()
        ]

        create_sql = f'CREATE TABLE IF NOT EXISTS {self.table_name} (' \
            + f'{", ".join(definition_strings + ["pk INTEGER PRIMARY KEY"])}' \
            + ')'

        with self.connect() as con:
            cur = con.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            cur.execute(create_sql)
        con.close()

    def connect(self) -> Connection:
        return sqlite3.connect(
            self.db_file, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

    @staticmethod
    def _resolve_type(obj_type: type) -> str:
        if issubclass(UnionType, obj_type):
            obj_type = get_args(obj_type)
        if issubclass(str, obj_type):
            return 'TEXT'
        if issubclass(int, obj_type):
            return 'INTEGER'
        if issubclass(float, obj_type):
            return 'REAL'
        if issubclass(datetime, obj_type):
            return 'TIMESTAMP'
        return 'TEXT'

    def add(self, obj: T) -> int:
        if getattr(obj, 'pk', None) != 0:
            raise ValueError(f'trying to add object {obj} with filled `pk` attribute')
        names = ', '.join(self.fields.keys())
        place_holder = ', '.join("?" * len(self.fields))
        values = [getattr(obj, x) for x in self.fields]
        with self.connect() as con:
            cur = con.cursor()
            if len(self.fields) != 0:
                cur.execute(
                    f'INSERT INTO {self.table_name} ({names}) VALUES ({place_holder})',
                    values
                )
            else:  # specific case for table with only pk column
                cur.execute(f'INSERT INTO {self.table_name} DEFAULT VALUES')
            pk = cur.lastrowid
            obj.pk = pk if pk is not None else 0
        con.close()
        return obj.pk

    def get(self, pk: int) -> T | None:
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(
                f'SELECT * FROM {self.table_name} WHERE pk = ?',
                [pk]
            )
            res = cur.fetchall()
        con.close()
        return self.cls(*res[0]) if len(res) != 0 else None

    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(
                f'SELECT * FROM {self.table_name}'
            )
            res = cur.fetchall()
        con.close()
        res: list[T] = [self.cls(*obj) for obj in res]
        if where is not None:
            res = [obj for obj in res
                   if all(getattr(obj, attr) == value for attr, value in where.items())]
        return res

    def update(self, obj: T) -> None:
        if obj.pk == 0:
            raise ValueError('attempt to update object with unknown primary key')
        update_strings = [f'{name} = ?' for name in self.fields.keys()]
        if len(update_strings) == 0:
            return
        values = [getattr(obj, x) for x in self.fields]
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(
                f'UPDATE {self.table_name} SET {", ".join(update_strings)} WHERE pk = ?',
                values + [obj.pk]
            )
        con.close()

    def delete(self, pk: int) -> None:
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(
                f'DELETE FROM {self.table_name} WHERE pk = ?',
                [pk]
            )
            deleted_count = cur.rowcount
        con.close()
        if deleted_count == 0:
            raise KeyError('attempt to delete unexistent object')
