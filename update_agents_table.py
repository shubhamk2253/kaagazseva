import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

cur.execute("ALTER TABLE agents ADD COLUMN latitude REAL")
cur.execute("ALTER TABLE agents ADD COLUMN longitude REAL")

conn.commit()
conn.close()

print("Agents table updated successfully")
