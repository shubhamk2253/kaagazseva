import sqlite3
import os

AGENT_COMMISSION = float(os.getenv("AGENT_COMMISSION_PERCENT", "0.70"))

def get_db():
    conn = sqlite3.connect('database.db', timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def get_agent_earnings(agent_name):
    """Returns total earnings and completed tasks for agent"""
    with get_db() as conn:
        row = conn.execute("""
            SELECT
                SUM(p.amount * ?) as earnings,
                COUNT(a.id) as tasks
            FROM applications a
            JOIN payments p ON a.application_id = p.application_id
            WHERE a.agent=? AND a.payment_status='Paid'
        """, (AGENT_COMMISSION, agent_name)).fetchone()

    return {
        "agent": agent_name,
        "earnings": row['earnings'] or 0,
        "tasks": row['tasks']
    }
