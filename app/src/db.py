from flask import g, session
import sqlite3
from pathlib import Path
import os


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
        g.db = sqlite3.connect(session['DATABASE'])
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


def init_db(db_path: str | Path, load_sample: bool = True):
    '''
    Description
    -----------
    Create sqlite file, create schema and load sample data (option)

    Parameters
    ---------
    db_path: str | Path
    Path for the db file

    load_sample: bool. Default True
    whether or not to load sample data into database.

    Returns
    --------
    None
    '''
    if not os.path.exists(Path(db_path).parent):
        raise FileExistsError
    db = sqlite3.connect(db_path)
    with open('app/schema.sql', encoding='utf-8') as f:
        db.executescript(f.read())
    if load_sample:
        with open('app/sample_data.sql', encoding='utf-8') as f:
            db.executescript(f.read())
