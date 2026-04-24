import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "data" / "maintenance.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS maintenance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                mileage_km INTEGER NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                cost_eur REAL NOT NULL DEFAULT 0,
                notes TEXT DEFAULT ''
            )
            """
        )
        conn.commit()
