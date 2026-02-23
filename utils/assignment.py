import os
import math
from sqlalchemy import text
from models import db

MAX_AGENT_LOAD = int(os.getenv("MAX_AGENT_LOAD", "20"))
MAX_ASSIGN_DISTANCE_KM = float(os.getenv("MAX_ASSIGN_DISTANCE_KM", "50"))


# =========================================================
# DISTANCE FUNCTION (Haversine)
# =========================================================
def distance_km(lat1, lon1, lat2, lon2):
    R = 6371

    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(d_lat / 2) ** 2 +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(d_lon / 2) ** 2
    )

    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))


# =========================================================
# MAIN ASSIGN FUNCTION (THIS IS IMPORTANT)
# =========================================================
def assign_best_agent(application_id, customer_pincode):

    # 1️⃣ Get customer coordinates from pincodes table
    pin = db.session.execute(text("""
        SELECT latitude, longitude
        FROM pincodes
        WHERE pincode = :pin
    """), {"pin": customer_pincode}).fetchone()

    customer_lat = None
    customer_lon = None

    if pin and pin.latitude and pin.longitude:
        customer_lat = pin.latitude
        customer_lon = pin.longitude

    # 2️⃣ Get verified agents
    agents = db.session.execute(text("""
        SELECT id, pincode, latitude, longitude
        FROM agents
        WHERE is_verified = TRUE
    """)).fetchall()

    if not agents:
        return None

    eligible_agents = []

    # 3️⃣ GPS-based assignment (if available)
    if customer_lat and customer_lon:
        for agent in agents:
            if agent.latitude and agent.longitude:
                dist = distance_km(
                    customer_lat,
                    customer_lon,
                    agent.latitude,
                    agent.longitude
                )

                if dist <= MAX_ASSIGN_DISTANCE_KM:
                    eligible_agents.append((agent.id, dist))

    # 4️⃣ Fallback to pincode match
    if not eligible_agents:
        for agent in agents:
            if agent.pincode == customer_pincode:
                eligible_agents.append((agent.id, 0))

    if not eligible_agents:
        return None

    agent_ids = [a[0] for a in eligible_agents]

    # 5️⃣ Check workload
    loads = db.session.execute(text("""
        SELECT agent_id, COUNT(*) as load
        FROM applications
        WHERE agent_id = ANY(:agents)
        AND status != 'Completed'
        GROUP BY agent_id
    """), {"agents": agent_ids}).fetchall()

    load_map = {row.agent_id: row.load for row in loads}

    for agent_id in agent_ids:
        load_map.setdefault(agent_id, 0)

    # 6️⃣ Capacity filter
    available = [
        (agent_id, dist)
        for agent_id, dist in eligible_agents
        if load_map[agent_id] < MAX_AGENT_LOAD
    ]

    if not available:
        return None

    # 7️⃣ Choose best agent
    selected_agent = min(
        available,
        key=lambda x: (load_map[x[0]], x[1])
    )[0]

    # 8️⃣ Update application
    db.session.execute(text("""
        UPDATE applications
        SET agent_id = :agent,
            status = 'Processing'
        WHERE application_id = :app
    """), {
        "agent": selected_agent,
        "app": application_id
    })

    db.session.commit()

    return selected_agent
