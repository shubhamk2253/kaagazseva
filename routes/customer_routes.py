from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from services.assignment_service import AssignmentService # For context
from repositories.application_repo import ApplicationRepository
from core.decorators import role_required
from core.responses import success_response

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/apply', methods=['POST'])
@role_required('customer')
def apply_service():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # We call repo directly for simple creates, or a service if logic is complex
    app = ApplicationRepository.create(
        customer_id=user_id,
        service_id=data.get('service_id'),
        pincode=data.get('pincode'),
        amount=data.get('amount')
    )
    
    return success_response(data={"application_id": app.id}, message="Application submitted")
