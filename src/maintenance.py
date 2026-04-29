from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.db import get_connection


@dataclass
class MaintenanceEntry:
    date: str
    mileage_km: int
    category: str
    description: str
    cost_eur: float
    notes: str = ""


def add_entry(entry: MaintenanceEntry) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO maintenance (
                date, mileage_km, category, description, cost_eur, notes
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                entry.date,
                entry.mileage_km,
                entry.category,
                entry.description,
                entry.cost_eur,
                entry.notes,
            ),
        )
        conn.commit()


def list_entries() -> Iterable[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, date, mileage_km, category, description, cost_eur, notes
            FROM maintenance
            ORDER BY date DESC, mileage_km DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def get_reminders() -> Iterable[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM reminders WHERE is_completed = 0 ORDER BY due_mileage ASC"
        ).fetchall()
    return [dict(row) for row in rows]


def get_vehicle_info() -> dict:
    with get_connection() as conn:
        rows = conn.execute("SELECT key, value FROM vehicle_info").fetchall()
    return {row["key"]: row["value"] for row in rows}


def update_vehicle_info(key: str, value: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO vehicle_info (key, value) VALUES (?, ?)", (key, value)
        )
        conn.commit()


def get_last_mileage_for_category(category: str) -> int | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT mileage_km FROM maintenance WHERE category = ? ORDER BY mileage_km DESC LIMIT 1",
            (category,),
        ).fetchone()
    return row["mileage_km"] if row else None


def save_log(filename: str, content: str, analysis_json: str) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO logs (filename, content, analysis_json) VALUES (?, ?, ?)",
            (filename, content, analysis_json),
        )
        conn.commit()
        return cursor.lastrowid


def list_logs() -> Iterable[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, filename, timestamp FROM logs ORDER BY timestamp DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def get_log(log_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM logs WHERE id = ?", (log_id,)
        ).fetchone()
    return dict(row) if row else None


def update_log_chat(log_id: int, chat_history_json: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE logs SET chat_history_json = ? WHERE id = ?",
            (chat_history_json, log_id),
        )
        conn.commit()


def add_fault(component: str, severity: str, description: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO faults (component, severity, description) VALUES (?, ?, ?)",
            (component, severity, description),
        )
        conn.commit()


def get_active_faults() -> Iterable[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM faults WHERE is_fixed = 0 ORDER BY detected_at DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def mark_fault_fixed(fault_id: int) -> None:
    with get_connection() as conn:
        conn.execute("UPDATE faults SET is_fixed = 1 WHERE id = ?", (fault_id,))
        conn.commit()


def delete_log(log_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM logs WHERE id = ?", (log_id,))
        conn.commit()
