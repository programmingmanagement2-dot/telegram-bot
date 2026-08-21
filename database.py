import sqlite3
from datetime import datetime


DB_NAME = "bot.db"


def connect_db():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = connect_db()
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
            user_id INTEGER,
            service TEXT,
            amount REAL,
            status TEXT,
            payment_reference TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def add_user(user_id, username, first_name):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO users
        (user_id, username, first_name, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        user_id,
        username,
        first_name,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def create_order(user_id, service, amount):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO orders
        (user_id, service, amount, status, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        service,
        amount,
        "Pending Payment",
        datetime.now().isoformat()
    ))

    order_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return order_id


def get_user_orders(user_id):
    conn = connect_db()
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
