PRAGMA foreign_keys = ON;

CREATE TABLE roles (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE users (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    login     TEXT NOT NULL UNIQUE,
    password  TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role_id   INTEGER NOT NULL REFERENCES roles(id)
);

CREATE TABLE categories    (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE);
CREATE TABLE manufacturers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE);
CREATE TABLE suppliers     (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE);
CREATE TABLE units         (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE);

-- id задаём из порядка строк в xlsx
CREATE TABLE pickup_points (
    id      INTEGER PRIMARY KEY,
    address TEXT NOT NULL UNIQUE
);

CREATE TABLE products (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    article         TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    category_id     INTEGER NOT NULL REFERENCES categories(id),
    description     TEXT,
    manufacturer_id INTEGER NOT NULL REFERENCES manufacturers(id),
    supplier_id     INTEGER NOT NULL REFERENCES suppliers(id),
    price           REAL    NOT NULL CHECK (price >= 0),
    unit_id         INTEGER NOT NULL REFERENCES units(id),
    stock_quantity  INTEGER NOT NULL CHECK (stock_quantity >= 0),
    discount        INTEGER NOT NULL DEFAULT 0 CHECK (discount BETWEEN 0 AND 100),
    photo_path      TEXT
);

CREATE TABLE orders (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES users(id),
    order_date      TEXT NOT NULL,
    delivery_date   TEXT,
    pickup_point_id INTEGER NOT NULL REFERENCES pickup_points(id),
    order_code      TEXT NOT NULL,
    status          TEXT NOT NULL
);

CREATE TABLE order_items (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id   INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity   INTEGER NOT NULL CHECK (quantity > 0)
);