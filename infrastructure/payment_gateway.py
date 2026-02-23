import razorpay
from flask import current_app

class RazorpayGateway:
    @staticmethod
    def _get_client():
        return razorpay.Client(
            auth=(current_app.config['RAZORPAY_KEY_ID'], current_app.config['RAZORPAY_KEY_SECRET'])
        )

    @staticmethod
    def create_order(amount_in_paisa, receipt_id):
        """Creates an official Razorpay Order."""
        client = RazorpayGateway._get_client()
        data = {
            "amount": amount_in_paisa,
            "currency": "INR",
            "receipt": receipt_id,
            "payment_capture": 1  # Auto-capture
        }
        return client.order.create(data=data)

    @staticmethod
    def verify_signature(order_id, payment_id, signature):
        """Verifies that the payment actually came from Razorpay."""
        client = RazorpayGateway._get_client()
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        try:
            client.utility.verify_payment_signature(params_dict)
            return True
        except Exception:
            return False
