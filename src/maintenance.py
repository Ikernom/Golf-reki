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
