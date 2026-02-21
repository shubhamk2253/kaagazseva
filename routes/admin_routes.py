from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from models import db
from sqlalchemy import text
from utils.security import role_required
import uuid

admin_bp = Blueprint('admin_bp', __name__)

# --- AGENT PAYOUT (FOUNDER ONLY) ---
@admin_bp.route("/api/admin/payout/<agent_id>", methods=["POST"])
@role_required("founder")
def payout_agent(agent_id):
    # Check agent wallet balance
    wallet = db.session.execute(text("""
        SELECT balance FROM agent_wallets WHERE agent_id = :id
    """), {"id": agent_id}).fetchone()

    if not wallet or wallet.balance <= 0:
        return jsonify({"message": "No balance available for payout"}), 400

    try:
        # Reset wallet balance to zero
        db.session.execute(text("""
            UPDATE agent_wallets SET balance = 0 WHERE agent_id = :id
        """), {"id": agent_id})
        
        # In production, add: INSERT INTO payout_history (agent_id, amount) VALUES (...)

        db.session.commit()
        return jsonify({"message": f"Payout of {wallet.balance} processed successfully"}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Payout failed", "details": str(e)}), 500


# --- GET PENDING AGENTS (FOUNDER & STATE ADMIN) ---
@admin_bp.route("/api/admin/pending-agents", methods=["GET"])
@role_required("founder") # Base security; logic below handles state_admin filtering
def get_pending_agents():
    user_id = get_jwt_identity()
    user = db.session.execute(text("SELECT role FROM users WHERE id = :id"), {"id": user_id}).fetchone()

    # Founder sees all pending agents
    if user.role == "founder":
        query = text("""
            SELECT id, full_name, mobile, email, state_id, created_at
            FROM agent_registrations WHERE status = 'pending'
            ORDER BY created_at DESC
        """)
        agents = db.session.execute(query).fetchall()

    # State Admin sees only their state's pending agents
    elif user.role == "state_admin":
        admin_data = db.session.execute(text("""
            SELECT state_id FROM agents WHERE id = :id
        """), {"id": user_id}).fetchone()

        if not admin_data:
            return jsonify({"error": "State Admin record not found"}), 404

        query = text("""
            SELECT id, full_name, mobile, email, state_id, created_at
            FROM agent_registrations 
            WHERE status = 'pending' AND state_id = :state_id
            ORDER BY created_at DESC
        """)
        agents = db.session.execute(query, {"state_id": admin_data.state_id}).fetchall()

    return jsonify([dict(a._mapping) for a in agents])


# --- APPROVE AGENT (FOUNDER & STATE ADMIN) ---
@admin_bp.route("/api/admin/approve-agent/<registration_id>", methods=["POST"])
@role_required("founder") # Base security; logic handles state validation
def approve_agent(registration_id):
    user_id = get_jwt_identity()
    admin = db.session.execute(text("SELECT role FROM users WHERE id = :id"), {"id": user_id}).fetchone()
    
    # Fetch the registration application
    reg = db.session.execute(text("SELECT * FROM agent_registrations WHERE id = :id"), {"id": registration_id}).fetchone()
    if not reg:
        return jsonify({"error": "Application not found"}), 404

    # Security: State Admin can only approve agents in their own state
    if admin.role == "state_admin":
        admin_state = db.session.execute(text("SELECT state_id FROM agents WHERE id = :id"), {"id": user_id}).fetchone()
        if not admin_state or reg.state_id != admin_state.state_id:
            return jsonify({"error": "Unauthorized for this state"}), 403

    try:
        new_agent_id = str(uuid.uuid4())
        
        # 1. Create the User
        db.session.execute(text("""
            INSERT INTO users (id, full_name, mobile, email, role)
            VALUES (:id, :name, :mobile, :email, 'agent')
        """), {"id": new_agent_id, "name": reg.full_name, "mobile": reg.mobile, "email": reg.email})

        # 2. Create Agent Profile
        db.session.execute(text("""
            INSERT INTO agents (id, state_id, district_id, is_verified)
            VALUES (:id, :state, :district, TRUE)
        """), {"id": new_agent_id, "state": reg.state_id, "district": reg.district_id})

        # 3. Initialize Wallet
        db.session.execute(text("""
            INSERT INTO agent_wallets (agent_id, balance) VALUES (:id, 0)
        """), {"id": new_agent_id})

        # 4. Update Registration Status
        db.session.execute(text("""
            UPDATE agent_registrations SET status='approved' WHERE id=:id
        """), {"id": registration_id})

        db.session.commit()
        return jsonify({"message": f"Agent {reg.full_name} approved", "agent_id": new_agent_id}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Approval failed", "details": str(e)}), 500


# --- REJECT AGENT ---
@admin_bp.route("/api/admin/reject-agent/<registration_id>", methods=["POST"])
@role_required("founder")
def reject_agent(registration_id):
    db.session.execute(text("""
        UPDATE agent_registrations SET status='rejected' WHERE id=:id
    """), {"id": registration_id})
    db.session.commit()
    return jsonify({"message": "Agent application rejected"}), 200

