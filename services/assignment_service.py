import sqlite3
import os
import math

MAX_AGENT_LOAD = int(os.getenv("MAX_AGENT_LOAD", "20"))
MAX_ASSIGN_DISTANCE_KM = float(os.getenv("MAX_ASSIGN_DISTANCE_KM", "50"))

def get_db():
    conn = sqlite3.connect('database.db', timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


# ---------- HAVERSINE DISTANCE ----------
def distance_km(lat1, lon1, lat2, lon2):
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(d_lat/2)**2 +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(d_lon/2)**2
    )
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))


# ---------- SELECT LEAST LOADED ----------
def _agent_loads(cur, agents):
    if not agents:
        return {}

    placeholders = ",".join(["?"] * len(agents))

    cur.execute(f"""
        SELECT agent, COUNT(*) as load
        FROM applications
        WHERE agent IN ({placeholders})
        AND status!='Completed'
        GROUP BY agent
    """, agents)

    loads = {r["agent"]: r["load"] for r in cur.fetchall()}

    for a in agents:
        loads.setdefault(a, 0)

    return loads


# ---------- MAIN AUTO ASSIGN ----------
def auto_assign_agent(app_id, customer_lat, customer_lon):

    with get_db() as conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT name, latitude, longitude
            FROM agents
            WHERE active=1
        """)
        agents = cur.fetchall()

        if not agents:
            return None

        # calculate distance for each agent
        nearby_agents = []
        for a in agents:
            if not a["latitude"] or not a["longitude"]:
                continue

            dist = distance_km(customer_lat, customer_lon, a["latitude"], a["longitude"])

            if dist <= MAX_ASSIGN_DISTANCE_KM:
                nearby_agents.append((a["name"], dist))

        if not nearby_agents:
            return None

        agent_names = [a[0] for a in nearby_agents]

        loads = _agent_loads(cur, agent_names)

        # filter by capacity
        available = [a for a in nearby_agents if loads[a[0]] < MAX_AGENT_LOAD]
        if not available:
            return None

        # scoring = workload + distance
        selected = min(
            available,
            key=lambda x: (loads[x[0]], x[1])
        )[0]

        cur.execute(
            "UPDATE applications SET agent=? WHERE application_id=?",
            (selected, app_id)
        )
        conn.commit()

        return selected
