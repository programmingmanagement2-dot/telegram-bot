import sqlite3
from datetime import datetime

DB_NAME = "bot.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            service TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'Pending',
            payment_status TEXT DEFAULT 'Unpaid',
            utr TEXT,
            created_at TEXT
        )
    """)

    # Existing databases ke liye missing columns safely add karo
    cursor.execute("PRAGMA table_info(orders)")
    columns = {row[1] for row in cursor.fetchall()}

    if "payment_status" not in columns:
        cursor.execute(
            "ALTER TABLE orders ADD COLUMN payment_status TEXT DEFAULT 'Unpaid'"
        )

    if "utr" not in columns:
        cursor.execute(
            "ALTER TABLE orders ADD COLUMN utr TEXT"
        )

    conn.commit()
    conn.close()


def add_user(user_id, username=None, first_name=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (user_id, username, first_name, created_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            first_name = excluded.first_name
    """, (
        user_id,
        username,
        first_name,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def create_order(user_id, service, amount):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO orders
        (user_id, service, amount, status, payment_status, created_at)
        VALUES (?, ?, ?, 'Pending', 'Unpaid', ?)
    """, (
        user_id,
        service,
        amount,
        datetime.now().isoformat()
    ))

    order_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return order_id


def get_user_orders(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, service, amount, status, created_at
        FROM orders
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))

    orders = cursor.fetchall()

    conn.close()

    return orders


def get_all_orders():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            user_id,
            service,
            amount,
            status,
            payment_status,
            utr,
            created_at
        FROM orders
        ORDER BY id DESC
    """)

    orders = cursor.fetchall()

    conn.close()

    return orders


def get_order(order_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            user_id,
            service,
            amount,
            status,
            payment_status,
            utr,
            created_at
        FROM orders
        WHERE id = ?
    """, (order_id,))

    order = cursor.fetchone()

    conn.close()

    return order


def update_order_status(order_id, status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE orders
        SET status = ?
        WHERE id = ?
    """, (status, order_id))

    conn.commit()
    conn.close()


def update_payment_status(order_id, payment_status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE orders
        SET payment_status = ?
        WHERE id = ?
    """, (payment_status, order_id))

    conn.commit()
    conn.close()


def save_utr(order_id, utr):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE orders
        SET utr = ?, payment_status = 'Verification Pending'
        WHERE id = ?
    """, (utr, order_id))

    conn.commit()
    conn.close()


def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, username, first_name, created_at
        FROM users
        ORDER BY created_at DESC
    """)

    users = cursor.fetchall()

    conn.close()

    return users
