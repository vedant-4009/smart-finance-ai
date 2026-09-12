"""
database.py
SQLite connection management and schema initialization for Smart Finance.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Iterator

import config


def get_connection() -> sqlite3.Connection:
    """Return a new SQLite connection with row factory set to dict-like rows."""
    conn = sqlite3.connect(config.DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def db_cursor() -> Iterator[sqlite3.Cursor]:
    """Context manager that yields a cursor and commits/rolls back automatically."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Create the users and expenses tables if they do not already exist."""
    with db_cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                expense_date TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses(user_id)")
