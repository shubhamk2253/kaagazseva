import os
import math
import uuid
from sqlalchemy import text
from models import db

MAX_AGENT_LOAD = int(os.getenv("MAX_AGENT_LOAD", "20"))
MAX_ASSIGN_DISTANCE_KM = float(os.getenv("MAX_ASSIGN_DISTANCE_KM", "50"))


# =========================================================
# 1️⃣ HAVERSINE DISTANCE
# =========================================================
def distance_km(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in KM

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
# 2️⃣ MAIN ASSIGN FUNCTION (Used by Payment Flow)
# =========================================================
def assign_best_agent(state_id, service_name):
    """
    Assign best available agent based on:
    - Verified status
    - Lowest workload
    """

    # Fetch verified agents in that state
    agents = db.session.execute(text("""
        SELECT id
        FROM agents
        WHERE is_verified = TRUE
        AND state_id = :state
    """), {"state": state_id}).fetchall()

    if not agents:
        return None

    agent_ids = [a.id for a in agents]

    # Build dynamic IN safely
    loads = db.session.execute(text("""
        SELECT agent_id, COUNT(*) as load
        FROM applications
        WHERE agent_id = ANY(:agents)
        AND status != 'Completed'
        GROUP BY agent_id
    """), {
        "agents": agent_ids
    }).fetchall()

    load_map = {row.agent_id: row.load for row in loads}

    for agent_id in agent_ids:
        load_map.setdefault(agent_id, 0)

    # Filter by capacity
    available_agents = [
        agent_id for agent_id in agent_ids
        if load_map[agent_id] < MAX_AGENT_LOAD
    ]

    if not available_agents:
        return None

    # Select lowest workload
    selected_agent = min(
        available_agents,
        key=lambda x: load_map[x]
    )

    return selected_agent
