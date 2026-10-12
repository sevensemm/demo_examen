import streamlit as st
import sqlite3
from db import query, execute, IMG_DIR, BASE

st.set_page_config(page_title="МебельОрг", layout="wide",
                   page_icon=str(IMG_DIR / "icon.png"))
st.markdown(
    "<style>html,body,[class*='css']{font-family:Calibri,sans-serif;}</style>",
    unsafe_allow_html=True
)

def current():
    return st.session_state.get("user")

def logout():
    st.session_state.user = None
    st.rerun()

def image_of(path):
    if path:
        p = IMG_DIR / path
        if p.exists():
            return str(p)
    return str(IMG_DIR / "picture.png")

# ---------- экран входа ----------
def login_page():
    st.image(str(IMG_DIR / "icon.png"), width=80)
    st.title("Вход в систему МебельОрг")
    with st.form("login"):
        login = st.text_input("Логин")
        pwd   = st.text_input("Пароль", type="password")
        ok    = st.form_submit_button("Войти")
    if ok:
        rows = query(
            """SELECT u.id, u.full_name, r.name AS role
               FROM users u JOIN roles r ON r.id = u.role_id
               WHERE u.login=? AND u.password=?""",
            (login, pwd)
        )
        if rows:
            st.session_state.user = rows[0]
            st.rerun()
        else:
            st.error("Неверный логин или пароль")
    if st.button("Войти как гость"):
        st.session_state.user = {"id": None, "full_name": "Гость", "role": "Гость"}
        st.rerun()

# ---------- карточка товара ----------
def render_card(p, admin=False):
    disc  = p["discount"]
    stock = p["stock_quantity"]
    price = p["price"]
    final = price * (1 - disc / 100)

    if stock == 0:
        bg = "#cccccc"
    elif disc > 15:
        bg = "#008080"
    else:
        bg = "#ffffff"

    if disc > 0:
        price_html = (f'<span style="color:red;text-decoration:line-through">'
                      f'{price:.2f}</span> '
                      f'<span style="color:black">{final:.2f}</span>')
    else:
        price_html = f"{price:.2f}"

    cols = st.columns([1, 3, 1])
    with cols[0]:
        st.image(image_of(p["photo_path"]), width=180)
    with cols[1]:
        st.markdown(
            f"""<div style="background:{bg};padding:10px;border-radius:6px">
            <b>{p['category']} | {p['name']}</b><br>
            Артикул: {p['article']}<br>
            Описание: {p['description'] or '-'}<br>
            Производитель: {p['manufacturer']}<br>
            Поставщик: {p['supplier']}<br>
            Цена: {price_html}<br>
            Ед. изм.: {p['unit']}<br>
            Количество на складе: {stock}
            </div>""",
            unsafe_allow_html=True
        )
    with cols[2]:
        st.markdown(f"<div style='text-align:center'>Скидка<br><b>{disc}%</b></div>",
                    unsafe_allow_html=True)
        if admin:
            if st.button("✏️", key=f"e{p['id']}"):
                st.session_state.edit_id = p["id"]
                st.rerun()
            if st.button("🗑️", key=f"d{p['id']}"):
                try:
                    execute("DELETE FROM products WHERE id=?", (p["id"],))
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("Нельзя удалить: товар присутствует в заказе")
    st.divider()

# ---------- форма добавления/редактирования ----------
def edit_form(pid=None):
    cats  = query("SELECT id, name FROM categories")
    mans  = query("SELECT id, name FROM manufacturers")
    sups  = query("SELECT id, name FROM suppliers")
    units = query("SELECT id, name FROM units")

    data = {"article": "", "name": "", "description": "",
            "price": 0.0, "stock_quantity": 0, "discount": 0, "photo_path": ""}
    if pid:
        r = query("SELECT * FROM products WHERE id=?", (pid,))
        if r:
            data = r[0]

    st.subheader("Редактирование товара" if pid else "Новый товар")
    article = st.text_input("Артикул", data["article"], disabled=bool(pid))
    name    = st.text_input("Наименование", data["name"])
    desc    = st.text_area("Описание", data.get("description") or "")
    cat     = st.selectbox("Категория",     cats,  format_func=lambda x: x["name"])
    man     = st.selectbox("Производитель", mans,  format_func=lambda x: x["name"])
    sup     = st.selectbox("Поставщик",     sups,  format_func=lambda x: x["name"])
    unit    = st.selectbox("Единица измерения", units, format_func=lambda x: x["name"])
    price   = st.number_input("Цена", min_value=0.0, value=float(data["price"]))
    stock   = st.number_input("Количество на складе", min_value=0,
                              value=int(data["stock_quantity"]))
    disc    = st.slider("Скидка %", 0, 100, int(data["discount"]))
    photo   = st.text_input("Имя файла фото", data.get("photo_path") or "")

    if st.button("Сохранить"):
        if price < 0 or stock < 0:
            st.error("Цена и количество не могут быть отрицательными")
            return
        if pid:
            execute(
                """UPDATE products SET name=?, description=?, category_id=?,
                   manufacturer_id=?, supplier_id=?, price=?, unit_id=?,
                   stock_quantity=?, discount=?, photo_path=? WHERE id=?""",
                (name, desc, cat["id"], man["id"], sup["id"], price,
                 unit["id"], stock, disc, photo, pid)
            )
        else:
            execute(
                """INSERT INTO products
                   (article, name, description, category_id, manufacturer_id,
                    supplier_id, price, unit_id, stock_quantity, discount, photo_path)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (article, name, desc, cat["id"], man["id"], sup["id"],
                 price, unit["id"], stock, disc, photo)
            )
        st.session_state.edit_id = None
        st.rerun()

# ---------- основная страница ----------
def products_page():
    u = current()
    role = u["role"]
    can_filter = role in ("Менеджер", "Администратор")
    is_admin   = role == "Администратор"

    c1, c2 = st.columns([6, 1])
    c1.title(f"Каталог товаров — {u['full_name']} ({role})")
    if c2.button("Выйти"):
        logout()

    search, sort_field, sort_dir, disc_range = "", "name", "asc", "Все диапазоны"
    if can_filter:
        f1, f2, f3, f4 = st.columns(4)
        search     = f1.text_input("Поиск")
        sort_field = f2.selectbox("Сортировать по", ["name", "price", "stock_quantity"])
        sort_dir   = f3.selectbox("Порядок", ["По возрастанию", "По убыванию"])
        disc_range = f4.selectbox("Скидка", ["Все диапазоны", "0-10.99%", "11-14.99%", "15% и более"])

    if is_admin:
        if st.button("➕ Добавить товар"):
            st.session_state.edit_id = "new"
            st.rerun()

    # форма поверх списка
    if st.session_state.get("edit_id") is not None:
        pid = st.session_state.edit_id
        edit_form(None if pid == "new" else pid)
        if st.button("Назад"):
            st.session_state.edit_id = None
            st.rerun()
        return

    sql = """
        SELECT p.*, c.name AS category, m.name AS manufacturer,
               s.name AS supplier, un.name AS unit
        FROM products p
        JOIN categories    c  ON c.id  = p.category_id
        JOIN manufacturers m  ON m.id  = p.manufacturer_id
        JOIN suppliers     s  ON s.id  = p.supplier_id
        JOIN units         un ON un.id = p.unit_id
        WHERE 1=1
    """
    params = []
    if search:
        sql += """ AND (p.name LIKE ? OR p.article LIKE ? OR p.description LIKE ?
                       OR c.name LIKE ? OR m.name LIKE ? OR s.name LIKE ?)"""
        like = f"%{search}%"
        params += [like] * 6
    if disc_range == "0-10.99%":
        sql += " AND p.discount < 11"
    elif disc_range == "11-14.99%":
        sql += " AND p.discount BETWEEN 11 AND 14"
    elif disc_range == "15% и более":
        sql += " AND p.discount >= 15"

    if can_filter:
        if sort_dir == 'По возрастанию':
            sql += f" ORDER BY p.{sort_field} ASC"
        else:
            sql += f" ORDER BY p.{sort_field} DESC"
    else:
        sql += " ORDER BY p.id"

    for p in query(sql, params):
        render_card(p, admin=is_admin)

# ---------- запуск ----------
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

if current() is None:
    login_page()
else:
    products_page()