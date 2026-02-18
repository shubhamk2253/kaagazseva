import sqlite3

DB = "database.db"

def get_db():
    conn = sqlite3.connect(DB, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


class UserModel:

    @staticmethod
    def find_by_username(username):
        with get_db() as conn:
            return conn.execute(
                "SELECT * FROM users WHERE username=?",
                (username,)
            ).fetchone()

    @staticmethod
    def create_user(username, password_hash, role):
        with get_db() as conn:
            conn.execute(
                "INSERT INTO users(username, password_hash, role) VALUES(?,?,?)",
                (username, password_hash, role)
            )
            conn.commit()

    @staticmethod
    def update_last_login(username):
        with get_db() as conn:
            conn.execute(
                "UPDATE users SET last_login=CURRENT_TIMESTAMP WHERE username=?",
                (username,)
            )
            conn.commit()

    @staticmethod
    def change_password(username, new_hash):
        with get_db() as conn:
            conn.execute(
                "UPDATE users SET password_hash=? WHERE username=?",
                (new_hash, username)
            )
            conn.commit()
