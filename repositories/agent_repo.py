from models.agent import Agent
from extensions import db

class AgentRepository:
    @staticmethod
    def get_by_id(agent_id):
        return Agent.query.get(agent_id)

    @staticmethod
    def find_available_agents(pincode):
        """Finds verified agents in a specific pincode who aren't overloaded."""
        return Agent.query.filter_by(
            base_pincode=pincode, 
            is_verified=True
        ).filter(Agent.current_workload < Agent.max_workload).all()

    @staticmethod
    def update_workload(agent_id, increment=True):
        agent = Agent.query.get(agent_id)
        if agent:
            agent.current_workload += 1 if increment else -1
            db.session.commit()
        return agent
