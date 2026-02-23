# services/admin_service.py
from repositories.application_repo import ApplicationRepository
from repositories.agent_repo import AgentRepository
from services.assignment_service import AssignmentService
from core.errors import KaagazSevaException

class AdminService:
    @staticmethod
    def force_reassign(app_id, new_agent_id):
        """Manually moves a job from one agent to another (Overriding the AI)."""
        app = ApplicationRepository.get_by_id(app_id)
        old_agent_id = app.agent_id
        
        # 1. Update Application
        ApplicationRepository.update_status(app_id, status="assigned", agent_id=new_agent_id)
        
        # 2. Correct the Workloads
        if old_agent_id:
            AgentRepository.update_workload(old_agent_id, increment=False)
        AgentRepository.update_workload(new_agent_id, increment=True)
        
        return True

    @staticmethod
    def get_system_health():
        """Founder summary of the entire marketplace."""
        # Combined logic for Admin Control Tower
        pass
