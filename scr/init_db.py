import sqlite3
from db import DB_PATH, SQL_DIR

def init():
    if DB_PATH.exists():
        DB_PATH.unlink()
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    for f in ("schema.sql", "seed.sql"):
        c.executescript((SQL_DIR / f).read_text(encoding="utf-8"))
    c.commit()
    c.close()
    print("БД создана:", DB_PATH)

if __name__ == "__main__":
    init()