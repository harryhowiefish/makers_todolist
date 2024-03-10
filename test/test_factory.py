from app.flask_app import create_app
from flask import Flask, g


def test_create(tmp_path):
    app = create_app(instance_path=tmp_path)
    assert isinstance(app, Flask)
    assert not app.testing


def test_config(tmp_path):
    app = create_app({'TESTING': True}, instance_path=tmp_path)
    assert app.testing


def test_teardown(app):
    with app.test_client() as client:
        client.get('/')
        assert 'db' not in g
