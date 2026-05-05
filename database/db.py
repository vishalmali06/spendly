import os
import sqlite3

from werkzeug.security import generate_password_hash


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "spendly.db")

CATEGORIES = (
    "Food",
    "Transport",
    "Bills",
    "Health",
    "Entertainment",
    "Shopping",
    "Other",
)

_SEED_EXPENSES = [
    (12.50, "Food",          "2026-05-01", "Lunch at corner deli"),
    (45.00, "Transport",     "2026-05-02", "Monthly metro pass top-up"),
    (89.99, "Bills",         "2026-05-03", "Internet bill — May"),
    (30.00, "Health",        "2026-05-03", "Pharmacy — vitamins"),
    (18.75, "Entertainment", "2026-05-04", "Movie ticket"),
    (64.20, "Shopping",      "2026-05-04", "New running shoes"),
    ( 7.80, "Food",          "2026-05-05", "Morning coffee and pastry"),
    (15.00, "Other",         "2026-05-05", "Birthday card and gift wrap"),
]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    try:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    date TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
                """
            )
    finally:
        conn.close()


def create_user(name, email, password):
    conn = get_db()
    try:
        with conn:
            cur = conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, generate_password_hash(password)),
            )
            return cur.lastrowid
    finally:
        conn.close()


def get_user_by_email(email):
    conn = get_db()
    try:
        return conn.execute(
            "SELECT id, name, email, password_hash FROM users WHERE email = ?",
            (email,),
        ).fetchone()
    finally:
        conn.close()


def get_user_by_id(user_id):
    conn = get_db()
    try:
        return conn.execute(
            "SELECT id, name, email FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    finally:
        conn.close()


def seed_db():
    conn = get_db()
    try:
        with conn:
            row = conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()
            if row["n"] > 0:
                return

            cur = conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                ("Demo User", "demo@spendly.com", generate_password_hash("demo123")),
            )
            user_id = cur.lastrowid

            conn.executemany(
                "INSERT INTO expenses (user_id, amount, category, date, description) "
                "VALUES (?, ?, ?, ?, ?)",
                [(user_id, *row) for row in _SEED_EXPENSES],
            )
    finally:
        conn.close()
