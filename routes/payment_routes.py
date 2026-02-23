from flask import Blueprint, request
from services.payment_service import PaymentService
from core.responses import success_response, error_response

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/verify', methods=['POST'])
def verify_payment():
    data = request.get_json()
    
    try:
        PaymentService.verify_and_activate(
            order_id=data.get('razorpay_order_id'),
            payment_id=data.get('razorpay_payment_id'),
            signature=data.get('razorpay_signature'),
            app_id=data.get('application_id')
        )
        return success_response(message="Payment verified and agent assigned")
    except Exception as e:
        return error_response(message=str(e))
