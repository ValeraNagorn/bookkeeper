import os
from datetime import datetime

from bookkeeper.repository.sqlite_repository import SQLiteRepository
from tests.test_utils import DB_NAME

import pytest
from dataclasses import dataclass


@pytest.fixture
def custom_class():
    @dataclass
    class Custom:
        name: str
        test: str
        pk: int = 0

    return Custom


@pytest.fixture
def repo(custom_class):
    return SQLiteRepository[custom_class](DB_NAME, custom_class)


@pytest.fixture(scope='class', autouse=True)
def remove_db_file():
    yield
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)


def test_get_all_with_condition(repo, custom_class):
    objects = []
    for i in range(5):
        o = custom_class(str(i), 'test')
        print(o)
        repo.add(o)
        objects.append(o)
    print(*repo.get_all(), sep='\n')
    assert repo.get_all({'name': '0'}) == [objects[0]]
    assert repo.get_all({'test': 'test'}) == objects


def test_resolve_type(repo):
    assert repo._resolve_type(type('abc')) == 'TEXT'
    assert repo._resolve_type(type(1)) == 'INTEGER'
    assert repo._resolve_type(type(1.23)) == 'REAL'
    assert repo._resolve_type(type([])) == 'TEXT'
    assert repo._resolve_type(type(datetime.now())) == 'TIMESTAMP'
    assert repo._resolve_type(type(int | None)) == 'TEXT'


def test_crud(repo, custom_class):
    obj = custom_class('name', 'test')
    pk = repo.add(obj)
    assert obj.pk == pk
    assert repo.get(pk) == obj
    obj2 = custom_class('name2', 'test2')
    obj2.pk = pk
    repo.update(obj2)
    assert repo.get(pk) == obj2
    repo.delete(pk)
    assert repo.get(pk) is None
