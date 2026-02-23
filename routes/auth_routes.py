from flask import Blueprint, request
from services.auth_service import AuthService
from core.responses import success_response, error_response

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    phone = data.get('phone')
    otp = data.get('otp')
    
    try:
        result = AuthService.verify_otp_and_login(phone, otp)
        return success_response(data=result, message="Login successful")
    except Exception as e:
        return error_response(message=str(e), status_code=401)
