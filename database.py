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

        # 1. Applications table (force recreate during development)
        conn.execute("DROP TABLE IF EXISTS applications")

        conn.execute('''
        CREATE TABLE applications(
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

        # 2. Services table (CRITICAL FIX)
        conn.execute('''
        CREATE TABLE IF NOT EXISTS services(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT UNIQUE,
            price REAL
        )
        ''')

        # Seed default services/prices
        default_services = [
            ("PAN Card New", 300),
            ("PAN Card Correction", 250),
            ("PAN Aadhaar Linking", 100),
            ("New Passport Application", 1500),
            ("Passport Renewal", 1200),
            ("Income Certificate", 200),
            ("Caste Certificate", 200),
            ("Domicile Certificate", 200),
            ("Driving License New", 800),
            ("Vehicle RC Transfer", 1000)
        ]
        for service in default_services:
            conn.execute(
                "INSERT OR IGNORE INTO services (service_name, price) VALUES (?, ?)",
                service
            )

        # 3. Agents table
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

        # 4. Payments table
        conn.execute('''
        CREATE TABLE IF NOT EXISTS payments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id TEXT,
            amount REAL,
            payment_status TEXT,
            payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # 5. Users (admin + agent login)
        conn.execute('''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            role TEXT,
            last_login TIMESTAMP
        )
        ''')

        # 6. Audit logs
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

        # 7. JWT token blocklist
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