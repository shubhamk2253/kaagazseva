from flask import Blueprint, request
from services.analytics_service import AnalyticsService
from services.admin_service import AdminService
from core.decorators import role_required
from core.responses import success_response

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/stats', methods=['GET'])
@role_required('admin')
def get_stats():
    stats = AnalyticsService.get_founder_stats()
    return success_response(data=stats)

@admin_bp.route('/reassign', methods=['POST'])
@role_required('admin')
def reassign():
    data = request.get_json()
    AdminService.force_reassign(data.get('app_id'), data.get('agent_id'))
    return success_response(message="Agent reassigned manually")
