# services/agent_service.py
from repositories.agent_repo import AgentRepository
from core.errors import ValidationError

class AgentService:
    @staticmethod
    def register_agent(user_id, pincode, service_radius=10):
        """Initial registration for a new agent."""
        # Validate pincode exists in our serviceable area
        # from repositories.pincode_repo import PincodeRepository
        # if not PincodeRepository.is_serviceable(pincode):
        #     raise ValidationError("Pincode not currently serviceable")

        agent = AgentRepository.create(
            id=user_id,
            base_pincode=pincode,
            service_radius=service_radius
        )
        return agent

    @staticmethod
    def toggle_verification(agent_id, status):
        """Admin logic to verify or suspend an agent."""
        agent = AgentRepository.get_by_id(agent_id)
        if not agent:
            raise ResourceNotFoundError("Agent profile not found")
        
        agent.is_verified = status
        db.session.commit()
        return agent
