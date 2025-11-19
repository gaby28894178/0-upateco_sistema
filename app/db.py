import os
import sqlite3
from datetime import datetime
import hashlib
import secrets

DB_PATH = os.getenv("ELTATA_DB_PATH", os.path.join(os.getcwd(), "data.db"))


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT,
            available INTEGER NOT NULL DEFAULT 1
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            FOREIGN KEY(order_id) REFERENCES orders(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS auth_tokens (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            expires_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """
    )

    cur.execute("PRAGMA table_info(orders)")
    cols = [r["name"] for r in cur.fetchall()]
    if "driver_id" not in cols:
        cur.execute("ALTER TABLE orders ADD COLUMN driver_id INTEGER")

    cur.execute("SELECT COUNT(*) AS c FROM products")
    if cur.fetchone()["c"] == 0:
        cur.executemany(
            "INSERT INTO products(name, description, price, category, available) VALUES(?,?,?,?,?)",
            [
                ("Pizza Muzzarella", "Pizza clásica", 1800.0, "Pizzas", 1),
                ("Pizza Napolitana", "Tomate y ajo", 2000.0, "Pizzas", 1),
                ("Coca Cola 1.5L", "Bebida", 800.0, "Bebidas", 1),
            ],
        )

    cur.execute("SELECT COUNT(*) AS c FROM customers")
    if cur.fetchone()["c"] == 0:
        cur.executemany(
            "INSERT INTO customers(name, phone, address) VALUES(?,?,?)",
            [
                ("Juan Pérez", "11-1111-1111", ""),
                ("María López", "11-2222-2222", ""),
            ],
        )

    cur.execute("SELECT COUNT(*) AS c FROM drivers")
    if cur.fetchone()["c"] == 0:
        cur.executemany(
            "INSERT INTO drivers(name, phone) VALUES(?,?)",
            [
                ("Carlos Repartidor", "11-9999-0001"),
                ("Ana Repartidora", "11-9999-0002"),
            ],
        )

    conn.commit()
    conn.close()


ALLOWED_STATUSES = ["Pendiente", "En preparación", "Listo", "Entregado", "Cancelado"]


def now_iso() -> str:
    return datetime.utcnow().isoformat()


def hash_password(p: str) -> str:
    return hashlib.sha256(p.encode()).hexdigest()


def seed_admin():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS c FROM users")
    if cur.fetchone()["c"] == 0:
        cur.execute(
            "INSERT INTO users(username, password_hash, role) VALUES(?,?,?)",
            ("admin", hash_password("admin"), "admin"),
        )
        conn.commit()
    conn.close()


def create_token(user_id: int, days: int = 1) -> str:
    token = secrets.token_hex(16)
    expires = datetime.utcnow().timestamp() + days * 86400
    expires_iso = datetime.utcfromtimestamp(expires).isoformat()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO auth_tokens(token, user_id, expires_at) VALUES(?,?,?)",
        (token, user_id, expires_iso),
    )
    conn.commit()
    conn.close()
    return token


def validate_token(token: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT a.token, a.expires_at, u.id as user_id, u.username, u.role FROM auth_tokens a JOIN users u ON u.id = a.user_id WHERE a.token=?",
        (token,),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    try:
        exp = datetime.fromisoformat(row["expires_at"]).timestamp()
    except Exception:
        return None
    if exp < datetime.utcnow().timestamp():
        return None
    return {"id": row["user_id"], "username": row["username"], "role": row["role"]}


def revoke_token(token: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM auth_tokens WHERE token=?", (token,))
    changed = cur.rowcount > 0
    conn.commit()
    conn.close()
    return changed