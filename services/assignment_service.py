import os
import math
from sqlalchemy import text
from models import db

MAX_AGENT_LOAD = int(os.getenv("MAX_AGENT_LOAD", "20"))
MAX_ASSIGN_DISTANCE_KM = float(os.getenv("MAX_ASSIGN_DISTANCE_KM", "50"))

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


# ---------- MAIN AUTO ASSIGN ----------
def auto_assign_agent(app_id, customer_lat, customer_lon):

    # 1️⃣ Fetch active agents
    agents = db.session.execute(text("""
        SELECT id, latitude, longitude
        FROM agents
        WHERE is_verified = TRUE
    """)).fetchall()

    if not agents:
        return None

    nearby_agents = []

    # 2️⃣ Calculate distance
    for a in agents:
        if not a.latitude or not a.longitude:
            continue

        dist = distance_km(
            customer_lat,
            customer_lon,
            a.latitude,
            a.longitude
        )

        if dist <= MAX_ASSIGN_DISTANCE_KM:
            nearby_agents.append((a.id, dist))

    if not nearby_agents:
        return None

    agent_ids = [a[0] for a in nearby_agents]

    # 3️⃣ Get workload for those agents
    loads = db.session.execute(text("""
        SELECT agent_id, COUNT(*) as load
        FROM applications
        WHERE agent_id = ANY(:agents)
        AND status != 'completed'
        GROUP BY agent_id
    """), {
        "agents": agent_ids
    }).fetchall()

    load_map = {row.agent_id: row.load for row in loads}

    # default zero load
    for agent_id in agent_ids:
        load_map.setdefault(agent_id, 0)

    # 4️⃣ Filter by capacity
    available = [
        (agent_id, dist)
        for agent_id, dist in nearby_agents
        if load_map[agent_id] < MAX_AGENT_LOAD
    ]

    if not available:
        return None

    # 5️⃣ Choose best (lowest workload, then shortest distance)
    selected_agent = min(
        available,
        key=lambda x: (load_map[x[0]], x[1])
    )[0]

    # 6️⃣ Update application
    db.session.execute(text("""
        UPDATE applications
        SET agent_id = :agent
        WHERE application_id = :app
    """), {
        "agent": selected_agent,
        "app": app_id
    })

    db.session.commit()

    return selected_agent
