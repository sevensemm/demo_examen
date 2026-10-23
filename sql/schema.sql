PRAGMA foreign_keys = ON;

CREATE TABLE roles (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE users (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    login     TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    role_id   INTEGER NOT NULL REFERENCES roles(id)
);

CREATE TABLE categories (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL UNIQUE,
    subcategory   TEXT NOT NULL
);

CREATE TABLE manufacturers (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE models (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL UNIQUE,
    category_id     INTEGER NOT NULL REFERENCES categories(id),
    manufacturer_id INTEGER NOT NULL REFERENCES manufacturers(id),
    description     TEXT,
    composition     TEXT,
    price           REAL NOT NULL CHECK (price >= 0),
    image_path      TEXT
);

CREATE TABLE sizes (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    value REAL NOT NULL UNIQUE
);

CREATE TABLE stock_items (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id   INTEGER NOT NULL REFERENCES models(id),
    size_id    INTEGER NOT NULL REFERENCES sizes(id),
    quantity   INTEGER NOT NULL CHECK (quantity >= 0),
    UNIQUE (model_id, size_id)
);

CREATE TABLE orders (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    order_date TEXT NOT NULL,
    user_id    INTEGER NOT NULL REFERENCES users(id)
);

CREATE TABLE order_items (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id       INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    stock_item_id  INTEGER NOT NULL REFERENCES stock_items(id),
    quantity       INTEGER NOT NULL CHECK (quantity > 0),
    price_per_unit REAL NOT NULL CHECK (price_per_unit >= 0)
);