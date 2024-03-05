import os

import pytest
from app import create_app
from app.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'r',
          encoding='utf-8') as f:
    _data_sql = f.read()


@pytest.fixture
def app(tmp_path):
    DB_PATH = str(tmp_path / 'app.sqlite')

    app = create_app({
        'TESTING': True,
        'DATABASE': DB_PATH,
    })
    with app.app_context():
        init_db(str(tmp_path))
        db = get_db()
        db.executescript(_data_sql)

    yield app

    os.remove(DB_PATH)


@pytest.fixture
def app_context(app):
    with app.app_context():
        yield


@pytest.fixture
def client(app):
    yield app.test_client()
