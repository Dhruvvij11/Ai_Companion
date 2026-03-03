import os
import sqlite3
from contextlib import closing

from core import config

SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_connection(db_path=None):
    path = db_path or config.DB_PATH

    if path != ":memory:":
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=None):
    with open(SCHEMA_FILE, "r", encoding="utf-8") as file_obj:
        schema = file_obj.read()

    with closing(get_connection(db_path)) as conn:
        conn.executescript(schema)
        conn.commit()
