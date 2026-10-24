import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = os.getenv("DB_PATH", "leads.db")


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_user_id INTEGER NOT NULL,
            username TEXT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            service TEXT NOT NULL,
            comment TEXT NOT NULL,
            created_at TEXT NOT NULL
        )""")
        conn.execute("CREATE INDEX IF NOT EXISTS ix_leads_user ON leads(telegram_user_id)")


def save_lead(user_id: int, username: str | None, name: str, phone: str, service: str, comment: str) -> int:
    with connect() as conn:
        cursor = conn.execute("""INSERT INTO leads
            (telegram_user_id, username, name, phone, service, comment, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)""", (user_id, username, name, phone, service, comment,
            datetime.now(timezone.utc).isoformat()))
        return cursor.lastrowid


def delete_user_leads(user_id: int) -> int:
    with connect() as conn:
        cursor = conn.execute("DELETE FROM leads WHERE telegram_user_id = ?", (user_id,))
        return cursor.rowcount
