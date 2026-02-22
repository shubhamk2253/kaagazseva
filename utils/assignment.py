from sqlalchemy import text
from models import db

def assign_best_agent(state_id, service_name):

    agents = db.session.execute(text("""
        SELECT a.id, a.rating, a.active_orders,
               a.penalty_score, a.specialization
        FROM agents a
        WHERE a.state_id = :state
        AND a.is_verified = TRUE
    """), {"state": state_id}).fetchall()

    best_agent = None
    best_score = -9999

    for agent in agents:

        rating_score = agent.rating * 0.4
        workload_penalty = agent.active_orders * 0.15
        penalty = agent.penalty_score * 0.1

        specialization_bonus = 0.15 if service_name in (agent.specialization or []) else 0

        score = rating_score + specialization_bonus - workload_penalty - penalty

        if score > best_score:
            best_score = score
            best_agent = agent.id

    return best_agent
