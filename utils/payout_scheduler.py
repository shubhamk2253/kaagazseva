from sqlalchemy import text
from models import db
from datetime import datetime, timedelta

def run_daily_payout():

    eligible_agents = db.session.execute(text("""
        SELECT agent_id, SUM(amount) as total
        FROM wallet_transactions
        WHERE type='credit'
        AND created_at < NOW() - INTERVAL '1 day'
        GROUP BY agent_id
    """)).fetchall()

    for agent in eligible_agents:

        if agent.total <= 0:
            continue

        # Insert payout record
        db.session.execute(text("""
            INSERT INTO payouts (agent_id, amount)
            VALUES (:agent, :amount)
        """), {
            "agent": agent.agent_id,
            "amount": agent.total
        })

        # Deduct from wallet
        db.session.execute(text("""
            INSERT INTO wallet_transactions 
            (agent_id, amount, type)
            VALUES (:agent, :amount, 'debit')
        """), {
            "agent": agent.agent_id,
            "amount": agent.total
        })

    db.session.commit()
