from repositories.agent_repo import AgentRepository
from repositories.application_repo import ApplicationRepository
from core.errors import ValidationError

class AssignmentService:
    @staticmethod
    def assign_best_agent(app_id):
        app = ApplicationRepository.get_by_id(app_id)
        if not app:
            raise ValidationError("Application not found")
            
        # 1. Find agents in that pincode with capacity
        available_agents = AgentRepository.find_available_agents(app.pincode)
        
        if not available_agents:
            # Logic for "Escalation" or "Broadening Search Radius"
            return None 

        # 2. Simple Round-Robin or Load-based selection
        selected_agent = min(available_agents, key=lambda a: a.current_workload)
        
        # 3. Finalize Assignment
        ApplicationRepository.update_status(app_id, "assigned", agent_id=selected_agent.id)
        AgentRepository.update_workload(selected_agent.id, increment=True)
        
        return selected_agent.id
