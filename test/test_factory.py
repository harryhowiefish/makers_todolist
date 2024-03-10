from app.flask_app import create_app
from flask import Flask, g
import os


def test_create(tmp_path):
    app = create_app(instance_path=tmp_path)
    assert isinstance(app, Flask)
    assert not app.testing


def test_config(tmp_path):
    app = create_app({'TESTING': True}, instance_path=tmp_path)
    assert app.testing


def test_db_creation(tmp_path):
    app = create_app(instance_path=tmp_path)
    DB_PATH = str(tmp_path / 'app.sqlite')
    assert isinstance(app, Flask)
    assert os.path.exists(DB_PATH)


def test_teardown(app):
    with app.test_client() as client:
        client.get('/api/v1/tasks?id=1')
        assert 'db' not in g
