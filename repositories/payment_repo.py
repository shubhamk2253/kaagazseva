from models.payment import Payment
from extensions import db

class PaymentRepository:
    @staticmethod
    def create_payment_record(app_id, order_id, amount):
        payment = Payment(
            application_id=app_id,
            razorpay_order_id=order_id,
            amount=amount,
            status="created"
        )
        db.session.add(payment)
        db.session.commit()
        return payment

    @staticmethod
    def update_payment_success(order_id, payment_id):
        payment = Payment.query.filter_by(razorpay_order_id=order_id).first()
        if payment:
            payment.razorpay_payment_id = payment_id
            payment.status = "captured"
            db.session.commit()
        return payment
