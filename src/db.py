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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                due_mileage INTEGER,
                due_date TEXT,
                category TEXT,
                is_completed INTEGER DEFAULT 0
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vehicle_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL
            )
            """
        )
        # Tabla para categorías personalizadas
        conn.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')

        # Tabla de futuras modificaciones (Wishlist)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS future_mods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                estimated_cost REAL,
                category TEXT,
                priority TEXT DEFAULT 'Media',
                notes TEXT
            )
        ''')
        
        # Insertar por defecto si está vacía
        cursor = conn.execute("SELECT COUNT(*) as count FROM categories")
        if cursor.fetchone()['count'] == 0:
            defaults = ["Aceite", "Filtros", "Fluidos", "Distribución", "Frenos", "Suspensión", "Neumáticos", "Electrónica", "Otros"]
            for d in defaults:
                conn.execute("INSERT INTO categories (name) VALUES (?)", (d,))

        # Tabla para logs de VCDS
        conn.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                content TEXT NOT NULL,
                analysis_json TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Migración: Añadir chat_history_json si no existe
        try:
            conn.execute("ALTER TABLE logs ADD COLUMN chat_history_json TEXT")
        except sqlite3.OperationalError:
            # La columna ya existe, no hacemos nada
            pass
        
        # Tabla para averías detectadas por la IA
        conn.execute('''
            CREATE TABLE IF NOT EXISTS faults (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                component TEXT NOT NULL,
                severity TEXT DEFAULT 'WARNING',
                description TEXT,
                detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_fixed INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
