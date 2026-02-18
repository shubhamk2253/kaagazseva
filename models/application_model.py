import sqlite3

DB = "database.db"

def get_db():
    conn = sqlite3.connect(DB, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


class ApplicationModel:

    @staticmethod
    def create_application(data):
        with get_db() as conn:
            conn.execute("""
                INSERT INTO applications(
                    application_id, name, mobile, service,
                    pincode, filename, status, agent
                )
                VALUES(?,?,?,?,?,?,?,?)
            """, (
                data['application_id'],
                data['name'],
                data['mobile'],
                data['service'],
                data['pincode'],
                data['filename'],
                data.get('status', 'Submitted'),
                data.get('agent', '')
            ))
            conn.commit()

    @staticmethod
    def get_by_application_id(app_id):
        with get_db() as conn:
            return conn.execute(
                "SELECT * FROM applications WHERE application_id=?",
                (app_id,)
            ).fetchone()

    @staticmethod
    def assign_agent(app_id, agent):
        with get_db() as conn:
            conn.execute(
                "UPDATE applications SET agent=? WHERE application_id=?",
                (agent, app_id)
            )
            conn.commit()

    @staticmethod
    def update_status(app_id, status):
        with get_db() as conn:
            conn.execute(
                "UPDATE applications SET status=? WHERE application_id=?",
                (status, app_id)
            )
            conn.commit()

    @staticmethod
    def agent_workload(agent):
        with get_db() as conn:
            row = conn.execute("""
                SELECT COUNT(*) as total
                FROM applications
                WHERE agent=? AND status!='Completed'
            """, (agent,)).fetchone()
            return row["total"]
