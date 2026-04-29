import sqlite3
from datetime import datetime
from src.db import get_connection

class MaintenanceEntry:
    def __init__(self, date, mileage_km, category, description, cost_eur=0.0, notes="", id=None):
        self.id = id
        self.date = date
        self.mileage_km = mileage_km
        self.category = category
        self.description = description
        self.cost_eur = cost_eur
        self.notes = notes

def add_entry(date: str, mileage_km: int, category: str, description: str, cost: float, notes: str = "") -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO maintenance (date, mileage_km, category, description, cost_eur, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (date, mileage_km, category, description, cost, notes)
        )
        conn.commit()

def list_entries():
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM maintenance ORDER BY date DESC, mileage_km DESC")
        return [dict(row) for row in cursor.fetchall()]

def get_reminders():
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM reminders WHERE is_completed = 0")
        return [dict(row) for row in cursor.fetchall()]

def get_vehicle_info():
    with get_connection() as conn:
        cursor = conn.execute("SELECT key, value FROM vehicle_info")
        return {row['key']: row['value'] for row in cursor.fetchall()}

def update_vehicle_info(key: str, value: str):
    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO vehicle_info (key, value) VALUES (?, ?)",
            (key, str(value))
        )
        conn.commit()

def save_log(filename: str, content: str, analysis_json: str) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO logs (filename, content, analysis_json) VALUES (?, ?, ?)",
            (filename, content, analysis_json)
        )
        conn.commit()
        return cursor.lastrowid

def list_logs():
    with get_connection() as conn:
        cursor = conn.execute("SELECT id, filename, timestamp FROM logs ORDER BY timestamp DESC")
        return [dict(row) for row in cursor.fetchall()]

def get_log(log_id: int):
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM logs WHERE id = ?", (log_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_log_chat(log_id: int, chat_history_json: str):
    with get_connection() as conn:
        # Asegurar que la columna existe (migración rápida)
        try:
            conn.execute("ALTER TABLE logs ADD COLUMN chat_history_json TEXT")
        except:
            pass
        conn.execute("UPDATE logs SET chat_history_json = ? WHERE id = ?", (chat_history_json, log_id))
        conn.commit()

def get_last_mileage_for_category(category: str) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT MAX(mileage_km) as last_km FROM maintenance WHERE category = ?",
            (category,)
        )
        result = cursor.fetchone()
        return result['last_km'] if result and result['last_km'] else 0

def add_fault(component: str, severity: str, description: str):
    with get_connection() as conn:
        # Crear tabla si no existe
        conn.execute('''CREATE TABLE IF NOT EXISTS faults (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            component TEXT,
            severity TEXT,
            description TEXT,
            status TEXT DEFAULT 'ACTIVE',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        conn.execute(
            "INSERT INTO faults (component, severity, description) VALUES (?, ?, ?)",
            (component, severity, description)
        )
        conn.commit()

def get_active_faults():
    with get_connection() as conn:
        try:
            cursor = conn.execute("SELECT * FROM faults WHERE status = 'ACTIVE' ORDER BY timestamp DESC")
            return [dict(row) for row in cursor.fetchall()]
        except:
            return []

def mark_fault_fixed(fault_id: int):
    with get_connection() as conn:
        conn.execute("UPDATE faults SET status = 'FIXED' WHERE id = ?", (fault_id,))
        conn.commit()

def delete_log(log_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM logs WHERE id = ?", (log_id,))
        conn.commit()

def delete_entry(entry_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM maintenance WHERE id = ?", (entry_id,))
        conn.commit()

def update_entry(entry_id: int, date: str, mileage_km: int, description: str, category: str, cost: float, notes: str = "") -> None:
    with get_connection() as conn:
        conn.execute(
            """UPDATE maintenance 
               SET date = ?, mileage_km = ?, description = ?, category = ?, cost_eur = ?, notes = ?
               WHERE id = ?""",
            (date, mileage_km, description, category, cost, notes, entry_id)
        )
        conn.commit()


def list_categories():
    with get_connection() as conn:
        cursor = conn.execute("SELECT name FROM categories ORDER BY name ASC")
        return [row['name'] for row in cursor.fetchall()]


def add_category(name: str):
    with get_connection() as conn:
        try:
            conn.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            conn.commit()
        except:
            pass # Ya existe


def list_future_mods():
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT * FROM future_mods 
            ORDER BY CASE priority
                WHEN 'Alta' THEN 1
                WHEN 'Media' THEN 2
                WHEN 'Baja' THEN 3
                ELSE 4
            END ASC
        """)
        return [dict(row) for row in cursor.fetchall()]


def add_future_mod(description, estimated_cost, category, priority, notes=""):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO future_mods (description, estimated_cost, category, priority, notes)
               VALUES (?, ?, ?, ?, ?)""",
            (description, estimated_cost, category, priority, notes)
        )
        conn.commit()


def delete_future_mod(mod_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM future_mods WHERE id = ?", (mod_id,))
        conn.commit()


def update_future_mod(mod_id, description, estimated_cost, category, priority, notes):
    with get_connection() as conn:
        conn.execute(
            """UPDATE future_mods 
               SET description = ?, estimated_cost = ?, category = ?, priority = ?, notes = ?
               WHERE id = ?""",
            (description, estimated_cost, category, priority, notes, mod_id)
        )
        conn.commit()
def create_chat_session(title: str = "Nueva Consulta") -> int:
    with get_connection() as conn:
        cursor = conn.execute("INSERT INTO chat_sessions (title) VALUES (?)", (title,))
        conn.commit()
        return cursor.lastrowid

def save_chat_message(session_id: int, role: str, content: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO chat_messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content)
        )
        conn.commit()

def list_chat_sessions():
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM chat_sessions ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]

def get_chat_messages(session_id: int):
    with get_connection() as conn:
        cursor = conn.execute("SELECT role, content FROM chat_messages WHERE session_id = ? ORDER BY timestamp ASC", (session_id,))
        return [dict(row) for row in cursor.fetchall()]

def delete_chat_session(session_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
        conn.commit()
