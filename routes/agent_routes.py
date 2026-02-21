from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from database import get_db
import os

# --- INITIALIZATION ---
agent_bp = Blueprint('agent_bp', __name__)
AGENT_COMMISSION = float(os.getenv("AGENT_COMMISSION_PERCENT", "0.70"))

UPLOADS_DONE = "completed_docs"
os.makedirs(UPLOADS_DONE, exist_ok=True)


# ---------------- AGENT PROFILE ----------------
@agent_bp.route('/profile')
@jwt_required()
def profile():
    username = get_jwt_identity()
    with get_db() as conn:
        row = conn.execute(
            "SELECT username, role, last_login FROM users WHERE username=?",
            (username,)
        ).fetchone()

    return jsonify(dict(row))

from flask import Blueprint, request, jsonify
from sqlalchemy import text
from models import db

agent_bp = Blueprint("agent_bp", __name__)

@agent_bp.route("/api/agent-register", methods=["POST"])
def agent_register():
    data = request.json

    db.session.execute(text("""
        INSERT INTO agent_registrations 
        (full_name, mobile, email, state_id, district_id, address)
        VALUES (:name, :mobile, :email, :state, :district, :address)
    """), {
        "name": data["full_name"],
        "mobile": data["mobile"],
        "email": data["email"],
        "state": data["state_id"],
        "district": data["district_id"],
        "address": data["address"]
    })

    db.session.commit()

    return jsonify({"message": "Application submitted. Awaiting approval."})
# ---------------- WORKLOAD ----------------
@agent_bp.route('/workload')
@jwt_required()
def workload():
    agent = get_jwt_identity()
    with get_db() as conn:
        res = conn.execute("""
            SELECT COUNT(*) as pending
            FROM applications
            WHERE agent=? AND status!='Completed'
        """, (agent,)).fetchone()

    return jsonify({"pending_tasks": res['pending']})


# ---------------- EARNINGS SUMMARY ----------------
@agent_bp.route('/earnings/summary')
@jwt_required()
def earnings_summary():
    agent = get_jwt_identity()
    with get_db() as conn:
        res = conn.execute("""
            SELECT SUM(p.amount * ?) as total
            FROM applications a
            JOIN payments p ON a.application_id = p.application_id
            WHERE a.agent=? AND a.payment_status='Paid'
        """, (AGENT_COMMISSION, agent)).fetchone()

    return jsonify({"total_earnings": res['total'] or 0})


# ---------------- EARNINGS HISTORY ----------------
@agent_bp.route('/earnings/history')
@jwt_required()
def earnings_history():
    agent = get_jwt_identity()
    with get_db() as conn:
        rows = conn.execute("""
            SELECT a.application_id,
                   (p.amount * ?) as earned,
                   a.service,
                   a.created_at
            FROM applications a
            JOIN payments p ON a.application_id = p.application_id
            WHERE a.agent=? AND a.payment_status='Paid'
            ORDER BY a.created_at DESC
        """, (AGENT_COMMISSION, agent)).fetchall()

    return jsonify([dict(r) for r in rows])


# ---------------- MARK COMPLETED ----------------
@agent_bp.route('/complete/<app_id>', methods=['POST'])
@jwt_required()
def complete_task(app_id):
    agent = get_jwt_identity()

    # Fixed: Accessing the file from the request
    file = request.files.get("document")
    file_path = ""

    if file:
        filename = secure_filename(file.filename)
        # Using os.path.join for cross-platform safety
        file_path = os.path.join(UPLOADS_DONE, f"{app_id}_{filename}")
        file.save(file_path)

    with get_db() as conn:
        # The update ensures only the assigned agent can complete their own task
        conn.execute("""
            UPDATE applications
            SET status='Completed'
            WHERE application_id=? AND agent=?
        """, (app_id, agent))
        conn.commit()


    return jsonify(success=True)
