from models.wallet import WalletTransaction
from models.agent import Agent
from extensions import db

class WalletRepository:
    @staticmethod
    def add_transaction(agent_id, amount, txn_type, app_id=None):
        """Credits or Debits the agent and updates their running balance."""
        agent = Agent.query.get(agent_id)
        
        # Calculate new balance
        if txn_type == "CREDIT":
            agent.current_balance += amount
            agent.total_earnings += amount
        else:
            agent.current_balance -= amount

        txn = WalletTransaction(
            agent_id=agent_id,
            application_id=app_id,
            amount=amount,
            transaction_type=txn_type,
            running_balance=agent.current_balance
        )
        
        db.session.add(txn)
        db.session.commit()
        return txn
