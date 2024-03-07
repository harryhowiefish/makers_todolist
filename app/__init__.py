from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('dev_config.py', silent=True)

    if test_config:
        app.config.from_mapping(**test_config)
    from . import db, todo, api
    db.init_db(app.instance_path)
    app.teardown_appcontext(db.close_db)

    app.register_blueprint(todo.bp)
    app.register_blueprint(api.bp)

    return app
