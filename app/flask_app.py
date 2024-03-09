from flask import Flask
from app.src import db, todo, api
from pathlib import Path
import os
import secrets


def create_app(test_config: dict = None):
    app = Flask(__name__, instance_relative_config=True)

    # check and create instance path
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)
    app.config['DATABASE'] = Path(app.instance_path) / 'app.sqlite'

    # check and create basic_config.py
    config_path = Path(app.instance_path) / 'basic_config.py'
    if not os.path.exists(config_path):
        with open(config_path, 'w') as f:
            f.write(f'SECRET_KEY = "{secrets.token_hex()}"')
    app.config.from_pyfile('basic_config.py')

    # if dev_config.py exist, it will overwrite existing configs
    app.config.from_pyfile('dev_config.py', silent=True)

    # if test_config is provided, don't init_db
    if test_config:
        app.config.from_mapping(**test_config)
    else:
        db.init_db(app.instance_path)

    # close db after request call
    app.teardown_appcontext(db.close_db)

    # include blueprints
    app.register_blueprint(todo.bp)
    app.register_blueprint(api.bp)

    return app


if __name__ == '__main__':
    app = create_app()
