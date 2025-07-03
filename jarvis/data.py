import os
import sqlite3
from typing import Optional


class DataManager:
    """Manage persistent data storage for JARVIS."""

    DB_PATH = os.path.join(os.path.dirname(__file__), "jarvis.db")
    _initialized = False

    @classmethod
    def init_db(cls) -> None:
        """Create required tables if they don't exist."""
        if cls._initialized:
            return
        conn = sqlite3.connect(cls.DB_PATH)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                speaker TEXT,
                message TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS environment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                temperature REAL,
                humidity REAL,
                pump INTEGER,
                gas_alert INTEGER
            )
            """
        )
        conn.commit()
        conn.close()
        cls._initialized = True

    @classmethod
    def log_conversation(cls, speaker: str, message: str) -> None:
        """Store a conversation entry."""
        cls.init_db()
        conn = sqlite3.connect(cls.DB_PATH)
        conn.execute(
            "INSERT INTO conversations (speaker, message) VALUES (?, ?)",
            (speaker, message),
        )
        conn.commit()
        conn.close()

    @classmethod
    def log_environment(
        cls,
        temperature: Optional[float],
        humidity: Optional[float],
        pump: Optional[bool] = None,
        gas_alert: Optional[bool] = None,
    ) -> None:
        """Store environmental measurements."""
        cls.init_db()
        conn = sqlite3.connect(cls.DB_PATH)
        conn.execute(
            """
            INSERT INTO environment (temperature, humidity, pump, gas_alert)
            VALUES (?, ?, ?, ?)
            """,
            (
                temperature,
                humidity,
                int(bool(pump)) if pump is not None else None,
                int(bool(gas_alert)) if gas_alert is not None else None,
            ),
        )
        conn.commit()
        conn.close()

    @classmethod
    def average_temperature(cls) -> Optional[float]:
        """Return the average temperature from logged data."""
        cls.init_db()
        conn = sqlite3.connect(cls.DB_PATH)
        cur = conn.execute(
            "SELECT AVG(temperature) FROM environment WHERE temperature IS NOT NULL"
        )
        value = cur.fetchone()[0]
        conn.close()
        return value

    @classmethod
    def average_humidity(cls) -> Optional[float]:
        """Return the average humidity from logged data."""
        cls.init_db()
        conn = sqlite3.connect(cls.DB_PATH)
        cur = conn.execute(
            "SELECT AVG(humidity) FROM environment WHERE humidity IS NOT NULL"
        )
        value = cur.fetchone()[0]
        conn.close()
        return value


__all__ = ["DataManager"]
