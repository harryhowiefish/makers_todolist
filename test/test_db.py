from app import db
from flask import g
from sqlite3 import Connection
import pytest
import os


def test_get_db(app_context):
    assert 'db' not in g
    d = db.get_db()
    assert isinstance(d, Connection)
    assert 'db' in g


def test_close_db(app_context):
    db.get_db()
    assert 'db' in g
    db.close_db()
    assert 'db' not in g


class TestInitDb:
    @staticmethod
    def test_bad_path(app_context):
        with pytest.raises(FileExistsError):
            db.init_db('./bad_path')

    @staticmethod
    def test_file_created_with_path(app_context, tmp_path):
        db.init_db(tmp_path)
        assert os.path.exists(tmp_path / 'app.sqlite')

    @staticmethod
    def test_file_created_with_string(app_context, tmp_path):
        db.init_db(str(tmp_path))
        assert os.path.exists(tmp_path / 'app.sqlite')

    @staticmethod
    def test_correct_schema(app_context, tmp_path):
        db.init_db(tmp_path)
        d = db.get_db()
        result = d.execute('''SELECT name FROM sqlite_master
                              WHERE type='table' AND
                              name!='sqlite_sequence';''').fetchall()
        table_names = [item['name'] for item in result]
        assert table_names == ['task']
