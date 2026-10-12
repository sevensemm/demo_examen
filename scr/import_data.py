import sqlite3
from openpyxl import load_workbook
from db import BASE, DB_PATH

DATA = BASE / "data"

def get_or_create(cur, table, name):
    cur.execute(f"INSERT OR IGNORE INTO {table}(name) VALUES (?)", (name,))
    return cur.execute(f"SELECT id FROM {table} WHERE name=?", (name,)).fetchone()[0]

def iter_rows(path):
    """Возвращает только непустые строки, начиная со 2-й."""
    wb = load_workbook(path, read_only=True, data_only=True)
    rows = wb.active.iter_rows(values_only=True)
    next(rows, None)                # пропуск шапки
    for r in rows:
        if r and r[0] not in (None, ""):
            yield r

# ---- user_import.xlsx: Роль | ФИО | Логин | Пароль ----
def import_users(cur):
    for r in iter_rows(DATA / "user_import.xlsx"):
        role, full_name, login, password = r[0], r[1], r[2], r[3]
        rid = get_or_create(cur, "roles", role)
        cur.execute(
            "INSERT OR IGNORE INTO users(login, password, full_name, role_id) VALUES (?,?,?,?)",
            (login, password, full_name, rid)
        )

# ---- Tovar.xlsx: A Артикул | B Наименование | C Ед.изм | D Цена | E Поставщик |
#                  F Производитель | G Категория | H Скидка | I Кол-во | J Описание | K Фото ----
def import_products(cur):
    for r in iter_rows(DATA / "Tovar.xlsx"):
        article, name, unit, price, supplier, manufacturer = r[0], r[1], r[2], r[3], r[4], r[5]
        category, discount, stock, description, photo      = r[6], r[7], r[8], r[9], r[10]
        cid = get_or_create(cur, "categories",    category)
        mid = get_or_create(cur, "manufacturers", manufacturer)
        sid = get_or_create(cur, "suppliers",     supplier)
        uid = get_or_create(cur, "units",         unit)
        cur.execute(
            """INSERT OR IGNORE INTO products
               (article, name, category_id, description, manufacturer_id, supplier_id,
                price, unit_id, stock_quantity, discount, photo_path)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (article, name, cid, description, mid, sid,
             float(price or 0), uid, int(stock or 0), int(discount or 0), photo)
        )

# ---- Пункты выдачи: один столбец адресов, id = порядковый номер строки ----
def import_pickup_points(cur):
    idx = 1
    for r in iter_rows(DATA / "Пункты выдачи_import.xlsx"):
        addr = r[0]
        cur.execute("INSERT OR IGNORE INTO pickup_points(id, address) VALUES (?,?)", (idx, addr))
        idx += 1

# ---- Заказ_import.xlsx ----
def parse_items(s):
    parts = [p.strip() for p in str(s).split(",") if p.strip()]
    pairs = []
    for i in range(0, len(parts) - 1, 2):
        try:
            pairs.append((parts[i], int(parts[i + 1])))
        except ValueError:
            continue
    return pairs

def import_orders(cur):
    for r in iter_rows(DATA / "Заказ_import.xlsx"):
        num, items_str, odate, ddate = r[0], r[1], r[2], r[3]
        pp_id, fio, code, status     = r[4], r[5], r[6], r[7]

        u = cur.execute("SELECT id FROM users WHERE full_name=?", (fio,)).fetchone()
        if not u:
            print("  пользователь не найден:", fio)
            continue
        pp = cur.execute("SELECT id FROM pickup_points WHERE id=?", (int(pp_id),)).fetchone()
        if not pp:
            print("  пункт выдачи не найден:", pp_id)
            continue

        cur.execute(
            """INSERT OR IGNORE INTO orders
               (id, user_id, order_date, delivery_date, pickup_point_id, order_code, status)
               VALUES (?,?,?,?,?,?,?)""",
            (int(num), u[0], str(odate), str(ddate), int(pp_id), str(code), status)
        )
        for art, qty in parse_items(items_str):
            p = cur.execute("SELECT id FROM products WHERE article=?", (art,)).fetchone()
            if not p:
                print("  артикул не найден:", art)
                continue
            cur.execute(
                "INSERT INTO order_items(order_id, product_id, quantity) VALUES (?,?,?)",
                (int(num), p[0], qty)
            )

def main():
    c = sqlite3.connect(DB_PATH)
    cur = c.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    import_users(cur)
    import_products(cur)
    import_pickup_points(cur)
    import_orders(cur)
    c.commit()
    c.close()
    print("Импорт завершён")

if __name__ == "__main__":
    main()