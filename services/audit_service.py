import sqlite3
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt

def get_db():
    conn = sqlite3.connect('database.db', timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def log_audit(action, target_id=None):
    """Centralized enterprise audit logger"""
    username = "SYSTEM"
    role = "SYSTEM"

    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity:
            username = identity
            role = get_jwt().get("role", "UNKNOWN")
    except:
        pass

    with get_db() as conn:
        conn.execute("""
            INSERT INTO audit_logs(action, performer, role, target_id)
            VALUES(?,?,?,?)
        """, (action, username, role, target_id))
        conn.commit()
