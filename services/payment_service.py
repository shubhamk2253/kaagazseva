from infrastructure.payment_gateway import RazorpayGateway
from repositories.payment_repo import PaymentRepository
from repositories.application_repo import ApplicationRepository
from core.errors import PaymentError

class PaymentService:
    @staticmethod
    def verify_and_activate(order_id, payment_id, signature, app_id):
        # 1. Verify Signature (Security)
        is_valid = RazorpayGateway.verify_signature(order_id, payment_id, signature)
        if not is_valid:
            raise PaymentError("Fraudulent payment signature detected")
            
        # 2. Update Payment Record
        PaymentRepository.update_payment_success(order_id, payment_id)
        
        # 3. Update Application Status
        ApplicationRepository.update_status(app_id, "paid")
        
        return True
