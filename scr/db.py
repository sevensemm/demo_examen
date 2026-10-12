import sqlite3
from pathlib import Path

SCR_DIR = Path(__file__).resolve().parent
BASE = SCR_DIR.parent
DB_PATH  = BASE / "data" / "furniture.db"
IMG_DIR  = BASE / "data" / "images"
SQL_DIR  = BASE / "sql"

def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    return c

def query(sql, params=()):
    with conn() as c:
        return [dict(r) for r in c.execute(sql, params).fetchall()]

def execute(sql, params=()):
    with conn() as c:
        cur = c.execute(sql, params)
        c.commit()
        return cur.lastrowid