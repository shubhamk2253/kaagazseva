from models.application import Application
from extensions import db

class ApplicationRepository:
    @staticmethod
    def create(customer_id, service_id, pincode, amount, doc_url=None):
        app = Application(
            customer_id=customer_id,
            service_id=service_id,
            pincode=pincode,
            payment_amount=amount,
            document_url=doc_url
        )
        db.session.add(app)
        db.session.commit()
        return app

    @staticmethod
    def get_by_id(app_id):
        return Application.query.get(app_id)

    @staticmethod
    def update_status(app_id, status, agent_id=None):
        app = Application.query.get(app_id)
        if app:
            app.status = status
            if agent_id:
                app.agent_id = agent_id
            db.session.commit()
        return app

    @staticmethod
    def get_customer_history(customer_id):
        return Application.query.filter_by(customer_id=customer_id).all()
