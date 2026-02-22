from flask import Blueprint, request, jsonify
import razorpay, os
from sqlalchemy import text
from models import db
from services.notification_service import notify_payment_success
from utils.assignment import assign_best_agent

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

    try:
        # Verify Razorpay signature
        razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id": data['order_id'],
            "razorpay_payment_id": data['payment_id'],
            "razorpay_signature": data['signature']
        })

        # Get application details needed for assignment using SQLAlchemy
        row = db.session.execute(text("""
            SELECT mobile, state_id, service_name 
            FROM applications 
            WHERE application_id = :app_id
        """), {"app_id": data['application_id']}).mappings().fetchone()

        if not row:
            return jsonify({"error": "Application not found"}), 404

        # 1️⃣ Insert payment record
        db.session.execute(text("""
            INSERT INTO payments (application_id, amount, payment_status)
            VALUES (:app_id, :amount, 'Paid')
        """), {
            "app_id": data['application_id'],
            "amount": data['amount']
        })

        # 2️⃣ Assign best agent
        agent_id = assign_best_agent(row["state_id"], row["service_name"])

        # 3️⃣ Update application
        db.session.execute(text("""
            UPDATE applications
            SET payment_status='Paid',
                agent_id=:agent,
                status='processing'
            WHERE application_id=:app_id
        """), {
            "agent": agent_id,
            "app_id": data['application_id']
        })

        db.session.commit()

        # Notify customer
        notify_payment_success(row["mobile"], data['application_id'], data['amount'])

        return jsonify(success=True, agent_id=agent_id)

    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e)), 500
