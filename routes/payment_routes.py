from flask import Blueprint, request, jsonify
import razorpay
import os
import uuid
from sqlalchemy import text
from models import db
from services.notification_service import notify_payment_success
from utils.assignment import assign_best_agent

payment_bp = Blueprint("payment_bp", __name__)

# =========================================================
# Razorpay Configuration
# =========================================================
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

razorpay_client = razorpay.Client(
    auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
)


# =========================================================
# 1️⃣ CREATE ORDER
# =========================================================
@payment_bp.route("/payment/create-order", methods=["POST"])
def create_order():
    data = request.get_json()

    try:
        amount = int(float(data["amount"]) * 100)  # Convert to paise

        order = razorpay_client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1
        })

        return jsonify({
            "order_id": order["id"],
            "key": RAZORPAY_KEY_ID,
            "amount": amount
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================================
# 2️⃣ VERIFY PAYMENT
# =========================================================
@payment_bp.route("/payment/verify", methods=["POST"])
def verify_payment():
    data = request.get_json()

    try:
        # ---------------- Verify Razorpay Signature ----------------
        razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id": data["order_id"],
            "razorpay_payment_id": data["payment_id"],
            "razorpay_signature": data["signature"]
        })

        # ---------------- Fetch Application ----------------
        row = db.session.execute(text("""
            SELECT mobile, state_id, service
            FROM applications
            WHERE application_id = :app_id
        """), {"app_id": data["application_id"]}).fetchone()

        if not row:
            return jsonify({"error": "Application not found"}), 404

        # ---------------- Insert Payment Record ----------------
        db.session.execute(text("""
            INSERT INTO payments (
                id,
                application_id,
                amount,
                status,
                created_at
            )
            VALUES (
                :id,
                :app_id,
                :amount,
                'Paid',
                NOW()
            )
        """), {
            "id": str(uuid.uuid4()),  # UUID generated in Python (Supabase safe)
            "app_id": data["application_id"],
            "amount": data["amount"]
        })

        # ---------------- Assign Best Agent ----------------
        agent_id = assign_best_agent(row.state_id, row.service)

        # ---------------- Update Application ----------------
        db.session.execute(text("""
            UPDATE applications
            SET status = 'Processing',
                agent_id = :agent
            WHERE application_id = :app_id
        """), {
            "agent": agent_id,
            "app_id": data["application_id"]
        })

        db.session.commit()

        # ---------------- Notify Customer ----------------
        notify_payment_success(
            row.mobile,
            data["application_id"],
            data["amount"]
        )

        return jsonify({
            "success": True,
            "agent_id": agent_id
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
