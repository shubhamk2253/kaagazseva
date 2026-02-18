# backend/database.py

import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "database.db")


# ---------------- DB CONNECTION ----------------
def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- INITIALIZE DATABASE ----------------
def init_db():
    with get_db() as conn:

        # Applications table
        conn.execute('''
        CREATE TABLE IF NOT EXISTS applications(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id TEXT UNIQUE,
            name TEXT,
            mobile TEXT,
            service TEXT,
            pincode TEXT,
            filename TEXT,
            status TEXT,
            agent TEXT,
            payment_status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Agents table
        conn.execute('''
        CREATE TABLE IF NOT EXISTS agents(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            mobile TEXT UNIQUE,
            district TEXT,
            pincode TEXT,
            active INTEGER DEFAULT 0
        )
        ''')

        # Payments table
        conn.execute('''
        CREATE TABLE IF NOT EXISTS payments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id TEXT,
            amount REAL,
            payment_status TEXT,
            payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Users (admin + agent login)
        conn.execute('''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            role TEXT,
            last_login TIMESTAMP
        )
        ''')

        # Audit logs
        conn.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            performer TEXT,
            role TEXT,
            target_id TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # JWT token blocklist
        conn.execute('''
        CREATE TABLE IF NOT EXISTS token_blocklist(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jti TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Index for fast search
        conn.execute("CREATE INDEX IF NOT EXISTS idx_application_id ON applications(application_id)")

        conn.commit()
