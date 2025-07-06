import os
import sqlite3
from typing import List, Tuple

DB_PATH = os.environ.get("JARVIS_DB_PATH", "jarvis.db")


def init_db(db_path: str = DB_PATH) -> None:
    """Initialize the database and create tables if necessary."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def insert_message(role: str, content: str, db_path: str = DB_PATH) -> None:
    """Insert a chat message into the history table."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO history (role, content) VALUES (?, ?)", (role, content)
    )
    conn.commit()
    conn.close()


def fetch_last_messages(limit: int = 10, db_path: str = DB_PATH) -> List[Tuple[str, str]]:
    """Fetch the most recent chat messages."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT role, content FROM history ORDER BY id DESC LIMIT ?", (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


__all__ = ["init_db", "insert_message", "fetch_last_messages"]
