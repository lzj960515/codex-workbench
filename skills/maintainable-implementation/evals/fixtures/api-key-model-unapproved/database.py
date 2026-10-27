import sqlite3
from pathlib import Path

def open_database(path=":memory:"):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript(Path(__file__).with_name("schema.sql").read_text())
    return db
