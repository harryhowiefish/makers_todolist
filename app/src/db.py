from flask import g, current_app
import sqlite3
import os
from pathlib import Path


def get_db() -> sqlite3.Connection:
    '''
    Description
    -----------
    add db object to flask.g and also return it.

    Parameters
    ---------
    None

    Returns
    --------
    db: sqlite3.Connection
    '''
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE']
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")

    return g.db


def close_db(e=None):
    '''
    Description
    -----------
    Remove database connection from flask.g and close connection.

    Parameters
    ---------
    e: Any
    filler argument in order to use app.teardown_appcontext

    Returns
    --------
    None
    '''
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db(folder_path: str | Path, load_sample: bool = True):
    '''
    Description
    -----------
    Create sqlite file, create schema and load sample data (option)

    Parameters
    ---------
    folder_path: str | Path
    the folder where app.sqlite will locate.

    load_sample: bool. Default True
    whether or not to load sample data into database.

    Returns
    --------
    None
    '''
    if not os.path.exists(folder_path):
        raise FileExistsError("Path doesn't exist.")
    DB_PATH = Path(folder_path) / 'app.sqlite'
    if os.path.exists(DB_PATH):
        os.unlink(DB_PATH)
    db = sqlite3.connect(DB_PATH)
    with open('app/schema.sql', encoding='utf-8') as f:
        db.executescript(f.read())
    if load_sample:
        with open('app/sample_data.sql', encoding='utf-8') as f:
            db.executescript(f.read())
