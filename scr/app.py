import streamlit as st
import sqlite3
from db import query, execute, IMG_DIR, BASE

st.set_page_config(page_title="Чудо Обувь", layout="wide",
                   page_icon=str(IMG_DIR / "Чудо Обувь.ico"))
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

# ---------- Вход ----------
def login_page():
    st.image(str(IMG_DIR / "Чудо Обувь.png"), width=120)
    st.title("Вход в систему «Чудо Обувь»")
    with st.form("login"):
        login = st.text_input("Логин")
        ok    = st.form_submit_button("Войти")
    if ok:
        rows = query(
            """SELECT u.id, u.full_name, r.name AS role
               FROM users u JOIN roles r ON r.id = u.role_id
               WHERE u.login=?""",
            (login,)
        )
        if rows:
            st.session_state.user = rows[0]
            st.rerun()
        else:
            st.error("Такого логина нет в системе")
    if st.button("Войти как неавторизованный пользователь"):
        st.session_state.user = {"id": None, "full_name": "Гость",
                                 "role": "Неавторизованный пользователь"}
        st.rerun()

# ---------- Каталог ----------
def render_model(m):
    stock_sum = sum(s["quantity"] for s in m["stocks"])
    bg = "#ff8080" if stock_sum <= 3 else "#ffffff"

    cols = st.columns([1, 3, 1])
    with cols[0]:
        st.image(image_of(m["image_path"]), width=160)
    with cols[1]:
        sizes = ", ".join(f"{s['value']} ({s['quantity']})" for s in m["stocks"]) or "нет в наличии"
        st.markdown(
            f"""<div style="background:{bg};padding:10px;border-radius:6px">
            <b>{m['category']} | {m['name']}</b><br>
            Производство: {m['manufacturer']}<br>
            Состав: {m['composition'] or '-'}<br>
            Описание: {m['description'] or '-'}<br>
            Цена: {m['price']:.2f} ₽<br>
            Размеры: {sizes}<br>
            Всего на складе: {stock_sum}
            </div>""",
            unsafe_allow_html=True
        )
    return stock_sum

def products_page():
    u = current()
    role = u["role"]
    can_filter = role != "Неавторизованный пользователь"
    is_staff   = role in ("Менеджер", "Администратор")

    c1, c2 = st.columns([6, 1])
    c1.title(f"Каталог обуви — {u['full_name']} ({role})")
    if c2.button("Выйти"):
        logout()

    search, sort_field, sort_dir = "", "name", "asc"
    if can_filter:
        f1, f2, f3 = st.columns(3)
        search     = f1.text_input("Поиск")
        sort_field = f2.selectbox("Сортировать по", ["name", "price"])
        sort_dir   = f3.selectbox("Порядок", ["asc", "desc"])

    # Получаем модели с категориями
    sql = """
        SELECT m.*, c.name AS category, c.subcategory, mn.name AS manufacturer
        FROM models m
        JOIN categories    c  ON c.id  = m.category_id
        JOIN manufacturers mn ON mn.id = m.manufacturer_id
        WHERE 1=1
    """
    params = []
    if search:
        sql += """ AND (m.name LIKE ? OR m.description LIKE ?
                       OR c.name LIKE ? OR c.subcategory LIKE ? OR mn.name LIKE ?)"""
        like = f"%{search}%"
        params += [like] * 5
    
    if can_filter:
        sql += f" ORDER BY m.{sort_field} {sort_dir.upper()}"
    else:
        sql += " ORDER BY m.id"

    models = query(sql, params)
    
    for m in models:
        # Подтягиваем остатки по размерам
        m["stocks"] = query(
            """SELECT s.value, si.quantity
               FROM stock_items si 
               JOIN sizes s ON s.id = si.size_id
               WHERE si.model_id=?
               ORDER BY s.value""",
            (m["id"],)
        )
        
        # Общее количество на складе по всем размерам
        total_stock = sum(s["quantity"] for s in m["stocks"])
        
        # Подсветка: если остаток <= 3, то красный фон #ff8080
        bg_color = "#ff8080" if total_stock <= 3 else "#ffffff"
        
        # Отрисовка
        cols = st.columns([1, 3, 1])
        with cols[0]:
            st.image(image_of(m["image_path"]), width=160)
            
        with cols[1]:
            sizes_str = ", ".join(f"{s['value']} ({s['quantity']} шт.)" for s in m["stocks"]) or "нет в наличии"
            
            st.markdown(
                f"""<div style="background:{bg_color}; padding:10px; border-radius:6px">
                <b>{m['category']} ({m['subcategory']}) | {m['name']}</b><br>
                Производство: {m['manufacturer']}<br>
                Состав: {m['composition'] or '-'}<br>
                Описание: {m['description'] or '-'}<br>
                Цена: {m['price']:.2f} ₽<br>
                Размеры: {sizes_str}<br>
                Всего на складе: {total_stock}
                </div>""",
                unsafe_allow_html=True
            )
        st.divider()

# ---------- Запуск ----------
if "user" not in st.session_state:
    st.session_state.user = None

if current() is None:
    login_page()
else:
    products_page()