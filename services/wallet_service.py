from repositories.wallet_repo import WalletRepository
from repositories.application_repo import ApplicationRepository
from core.constants import AGENT_COMMISSION_PERCENT
from extensions import db

class WalletService:
    @staticmethod
    def process_job_completion(app_id):
        app = ApplicationRepository.get_by_id(app_id)
        
        # Ensure it's not already paid out
        if app.status == "completed":
            return False

        # Calculate Split
        agent_earnings = (app.payment_amount * AGENT_COMMISSION_PERCENT) / 100
        
        try:
            # ATOMIC OPERATION
            WalletRepository.add_transaction(
                agent_id=app.agent_id,
                amount=agent_earnings,
                txn_type="CREDIT",
                app_id=app.id
            )
            ApplicationRepository.update_status(app_id, "completed")
            return True
        except Exception as e:
            db.session.rollback()
            raise e
