from flask import Blueprint, request, jsonify
import razorpay, os
from database import get_db
from services.assignment_service import auto_assign_agent
from services.notification_service import notify_payment_success

payment_bp = Blueprint('payment_bp', __name__)

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

razorpay_client = razorpay.Client(
    auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
)

# ---------------- CREATE ORDER ----------------
@payment_bp.route('/create-order', methods=['POST'])
def create_order():
    data = request.get_json()

    amount = int(float(data['amount']) * 100)

    order = razorpay_client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    return jsonify({
        "order_id": order['id'],
        "key": RAZORPAY_KEY_ID,
        "amount": amount
    })


# ---------------- VERIFY PAYMENT ----------------
@payment_bp.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()

    razorpay_client.utility.verify_payment_signature({
        "razorpay_order_id": data['order_id'],
        "razorpay_payment_id": data['payment_id'],
        "razorpay_signature": data['signature']
    })

    with get_db() as conn:
        conn.execute(
            "INSERT INTO payments(application_id, amount, payment_status) VALUES(?,?,?)",
            (data['application_id'], data['amount'], "Paid")
        )

        conn.execute(
            "UPDATE applications SET payment_status='Paid' WHERE application_id=?",
            (data['application_id'],)
        )

        row = conn.execute(
            "SELECT mobile, pincode FROM applications WHERE application_id=?",
            (data['application_id'],)
        ).fetchone()

        mobile = row["mobile"]
        pincode = row["pincode"]

        conn.commit()

    # Assign agent
    agent = auto_assign_agent(data['application_id'], pincode)

    # Notify customer
    notify_payment_success(mobile, data['application_id'], data['amount'])

    return jsonify(success=True, agent=agent)
