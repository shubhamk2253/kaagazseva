from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from services.wallet_service import WalletService
from core.decorators import role_required
from core.responses import success_response, error_response

agent_bp = Blueprint('agent', __name__)

@agent_bp.route('/complete-job', methods=['POST'])
@role_required('agent')
def complete_job():
    data = request.get_json()
    app_id = data.get('application_id')
    
    try:
        WalletService.process_job_completion(app_id)
        return success_response(message="Job marked as complete and earnings credited")
    except Exception as e:
        return error_response(message=str(e))
