import sqlite3
import os
DB_PATH = 'instance/app.sqlite'
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
db = sqlite3.connect(DB_PATH)
with open('app/schema.sql', encoding='utf-8') as f:
    db.executescript(f.read())
