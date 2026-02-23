from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from sqlalchemy import text
from models import db
from datetime import datetime
import os
import uuid

agent_bp = Blueprint("agent_bp", __name__)

# ---------------- FILE UPLOAD CONFIG ----------------
UPLOADS_DONE = "completed_docs"
os.makedirs(UPLOADS_DONE, exist_ok=True)


# =========================================================
# 1️⃣ AGENT REGISTRATION (Public)
# =========================================================
@agent_bp.route("/agent-register", methods=["POST"])
def agent_register():
    data = request.json

    try:
        db.session.execute(text("""
            INSERT INTO agent_registrations
            (id, full_name, mobile, email, state_id, district_id, address, status, created_at)
            VALUES (:id, :name, :mobile, :email, :state, :district, :address, 'pending', NOW())
        """), {
            "id": str(uuid.uuid4()),
            "name": data["full_name"],
            "mobile": data["mobile"],
            "email": data["email"],
            "state": data["state_id"],
            "district": data["district_id"],
            "address": data["address"]
        })

        db.session.commit()
        return jsonify({"message": "Application submitted. Awaiting approval."}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# =========================================================
# 2️⃣ AGENT PROFILE
# =========================================================
@agent_bp.route("/agent/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()

    row = db.session.execute(text("""
        SELECT full_name, role, email, mobile
        FROM users
        WHERE id = :id
    """), {"id": user_id}).fetchone()

    if not row:
        return jsonify({"error": "User not found"}), 404

    return jsonify(dict(row._mapping))


# =========================================================
# 3️⃣ AGENT WORKLOAD
# =========================================================
@agent_bp.route("/agent/workload", methods=["GET"])
@jwt_required()
def workload():
    agent_id = get_jwt_identity()

    res = db.session.execute(text("""
        SELECT COUNT(*) as pending
        FROM applications
        WHERE agent_id = :agent
        AND status != 'Completed'
    """), {"agent": agent_id}).fetchone()

    return jsonify({"pending_tasks": res.pending if res else 0})


# =========================================================
# 4️⃣ WALLET BALANCE
# =========================================================
@agent_bp.route("/agent/wallet", methods=["GET"])
@jwt_required()
def get_wallet():
    agent_id = get_jwt_identity()

    wallet = db.session.execute(text("""
        SELECT balance
        FROM agent_wallets
        WHERE agent_id = :id
    """), {"id": agent_id}).fetchone()

    return jsonify({
        "balance": float(wallet.balance) if wallet else 0.0
    })


# =========================================================
# 5️⃣ EARNINGS HISTORY
# =========================================================
@agent_bp.route("/agent/earnings-history", methods=["GET"])
@jwt_required()
def earnings_history():
    agent_id = get_jwt_identity()

    rows = db.session.execute(text("""
        SELECT application_id,
               service_charge,
               platform_commission,
               agent_payout,
               created_at
        FROM agent_earnings
        WHERE agent_id = :agent
        ORDER BY created_at DESC
    """), {"agent": agent_id}).fetchall()

    return jsonify([dict(r._mapping) for r in rows])


# =========================================================
# 6️⃣ COMPLETE APPLICATION
# =========================================================
@agent_bp.route("/agent/complete/<application_id>", methods=["POST"])
@jwt_required()
def complete_application(application_id):

    agent_id = get_jwt_identity()

    # Verify application ownership
    application = db.session.execute(text("""
        SELECT id, state_service_id
        FROM applications
        WHERE id = :id
        AND agent_id = :agent
        AND status != 'Completed'
    """), {
        "id": application_id,
        "agent": agent_id
    }).fetchone()

    if not application:
        return jsonify({"error": "Application not found or already completed"}), 403

    # Handle file upload
    file = request.files.get("document")
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(
            UPLOADS_DONE,
            f"{application_id}_{filename}"
        )
        file.save(file_path)

    # Get pricing configuration
    service = db.session.execute(text("""
        SELECT service_fee
        FROM state_services
        WHERE id = :id
    """), {"id": application.state_service_id}).fetchone()

    if not service:
        return jsonify({"error": "Service pricing missing"}), 500

    service_charge = float(service.service_fee)

    # Commission Logic (25% OR minimum 30)
    commission = max(service_charge * 0.25, 30.0)
    payout = service_charge - commission

    try:
        # Save earnings record
        db.session.execute(text("""
            INSERT INTO agent_earnings
            (agent_id, application_id, service_charge, platform_commission, agent_payout, created_at)
            VALUES (:agent, :app, :service_charge, :commission, :payout, NOW())
        """), {
            "agent": agent_id,
            "app": application_id,
            "service_charge": service_charge,
            "commission": commission,
            "payout": payout
        })

        # Wallet transaction log
        db.session.execute(text("""
            INSERT INTO wallet_transactions
            (agent_id, application_id, amount, tx_type, created_at)
            VALUES (:agent, :app, :amount, 'credit', NOW())
        """), {
            "agent": agent_id,
            "app": application_id,
            "amount": payout
        })

        # Update wallet (Postgres safe UPSERT)
        db.session.execute(text("""
            INSERT INTO agent_wallets (agent_id, balance)
            VALUES (:agent, :amount)
            ON CONFLICT (agent_id)
            DO UPDATE SET balance = agent_wallets.balance + :amount
        """), {
            "agent": agent_id,
            "amount": payout
        })

        # Mark application completed
        db.session.execute(text("""
            UPDATE applications
            SET status='Completed',
                updated_at=NOW()
            WHERE id=:id
        """), {"id": application_id})

        db.session.commit()

        return jsonify({
            "message": "Application completed successfully",
            "payout": payout
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Transaction failed",
            "details": str(e)
        }), 500
