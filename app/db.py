from flask import g, current_app
import sqlite3
import sys
import os
from pathlib import Path


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE']
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")

    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db(folder_path: str | Path):
    if not os.path.exists(folder_path):
        raise FileExistsError("Path doesn't exist.")
    DB_PATH = Path(folder_path) / 'app.sqlite'
    if os.path.exists(DB_PATH):
        os.unlink(DB_PATH)
    db = sqlite3.connect(DB_PATH)
    with open('app/schema.sql', encoding='utf-8') as f:
        db.executescript(f.read())


if __name__ == "__main__":
    init_db(sys.argv[1])
