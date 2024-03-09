from app.flask_app import create_app
from flask import Flask, g


def test_config():
    assert create_app({'TESTING': True}).testing


def test_create():
    app = create_app({'TESTING': True})
    assert isinstance(app, Flask)


def test_teardown(app):
    with app.test_client() as client:
        client.get('/api/v1/tasks?id=1')
        assert 'db' not in g
