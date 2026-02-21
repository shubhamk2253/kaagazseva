from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy import text
from models import db
from services.audit_service import log_audit

admin_bp = Blueprint('admin_bp', __name__)

# ---------- ROLE CHECK HELPER ----------
def admin_only():
    claims = get_jwt()
    # Allowing 'founder' or 'admin' roles to access these high-level functions
    return claims.get("role") in ["admin", "founder"]

# ---------- DASHBOARD STATS ----------
@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    if not admin_only():
        return jsonify({"success": False, "msg": "Forbidden"}), 403

    # Using text() for SQLAlchemy compatibility
    total_apps = db.session.execute(text("SELECT COUNT(*) FROM applications")).fetchone()[0]
    active_agents = db.session.execute(text("SELECT COUNT(*) FROM agents WHERE is_verified=TRUE")).fetchone()[0]
    revenue = db.session.execute(text("SELECT COALESCE(SUM(amount),0) FROM payments")).fetchone()[0]

    return jsonify({
        "success": True,
        "applications": total_apps,
        "active_agents": active_agents,
        "revenue": revenue
    })

# ---------- PENDING AGENT APPLICATIONS ----------
@admin_bp.route('/pending-agents', methods=['GET'])
@jwt_required()
def pending_agents():
    if not admin_only():
        return jsonify({"success": False, "msg": "Forbidden"}), 403

    # Fetching from the temporary registration table
    rows = db.session.execute(text("""
        SELECT id, full_name, mobile, district_id, state_id, created_at 
        FROM agent_registrations 
        WHERE status = 'pending'
    """)).fetchall()

    return jsonify([dict(r._mapping) for r in rows])

# ---------- ACTIVE AGENT LIST ----------
@admin_bp.route('/active-agents', methods=['GET'])
@jwt_required()
def active_agents():
    if not admin_only():
        return jsonify({"success": False, "msg": "Forbidden"}), 403

    rows = db.session.execute(text("""
        SELECT u.id, u.full_name, u.mobile, a.district_id, a.is_verified
        FROM users u
        JOIN agents a ON u.id = a.id
        WHERE u.role = 'agent' AND a.is_verified = TRUE
    """)).fetchall()

    return jsonify([dict(r._mapping) for r in rows])

# ---------- APPROVE AGENT (CRITICAL WORKFLOW) ----------
@admin_bp.route('/approve-agent/<agent_id>', methods=['POST'])
@jwt_required()
def approve_agent(agent_id):
    if not admin_only():
        return jsonify({"success": False, "msg": "Forbidden"}), 403

    # 1. Check if registration exists
    agent_reg = db.session.execute(text("""
        SELECT * FROM agent_registrations WHERE id = :id AND status = 'pending'
    """), {"id": agent_id}).fetchone()

    if not agent_reg:
        return jsonify({"error": "Pending application not found"}), 404

    try:
        # 2. Create the User Record
        # Note: using gen_random_uuid() as per your Postgres setup
        db.session.execute(text("""
            INSERT INTO users (id, full_name, mobile, email, role)
            VALUES (gen_random_uuid(), :name, :mobile, :email, 'agent')
        """), {
            "name": agent_reg.full_name,
            "mobile": agent_reg.mobile,
            "email": getattr(agent_reg, 'email', None) 
        })

        # 3. Retrieve the newly created user ID
        user = db.session.execute(text("""
            SELECT id FROM users WHERE mobile = :mobile
        """), {"mobile": agent_reg.mobile}).fetchone()

        # 4. Create the Agent Profile
        db.session.execute(text("""
            INSERT INTO agents (id, state_id, district_id, is_verified)
            VALUES (:id, :state, :district, TRUE)
        """), {
            "id": user.id,
            "state": agent_reg.state_id,
            "district": agent_reg.district_id
        })

        # 5. Mark registration as approved
        db.session.execute(text("""
            UPDATE agent_registrations
            SET status='approved'
            WHERE id=:id
        """), {"id": agent_id})

        db.session.commit()
        log_audit("AGENT_APPROVED", f"Agent: {agent_reg.full_name} | ID: {user.id}")

        return jsonify({"success": True, "message": "Agent approved and user created"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

# ---------- DISABLE AGENT ----------
@admin_bp.route('/disable-agent/<user_id>', methods=['POST'])
@jwt_required()
def disable_agent(user_id):
    if not admin_only():
        return jsonify({"success": False, "msg": "Forbidden"}), 403

    db.session.execute(text("""
        UPDATE agents SET is_verified = FALSE WHERE id = :id
    """), {"id": user_id})
    db.session.commit()

    log_audit("AGENT_DISABLED", user_id)
    return jsonify({"success": True, "message": "Agent access revoked"})

# ---------- ALL APPLICATIONS ----------
@admin_bp.route('/applications', methods=['GET'])
@jwt_required()
def all_applications():
    if not admin_only():
        return jsonify(msg="Forbidden"), 403

    rows = db.session.execute(text("""
        SELECT application_id, name, mobile, service,
               status, agent, payment_status, created_at
        FROM applications
        ORDER BY created_at DESC
    """)).fetchall()

    return jsonify([dict(r._mapping) for r in rows])

# ---------- REASSIGN AGENT ----------
@admin_bp.route('/reassign/<app_id>', methods=['POST'])
@jwt_required()
def reassign(app_id):
    if not admin_only():
        return jsonify(msg="Forbidden"), 403

    new_agent_id = request.json.get("agent_id")

    db.session.execute(text("""
        UPDATE applications SET agent = :agent_id WHERE application_id = :app_id
    """), {"agent_id": new_agent_id, "app_id": app_id})
    
    db.session.commit()
    log_audit("APPLICATION_REASSIGNED", app_id)
    return jsonify(success=True)

# ---------- CANCEL APPLICATION ----------
@admin_bp.route('/cancel/<app_id>', methods=['POST'])
@jwt_required()
def cancel(app_id):
    if not admin_only():
        return jsonify(msg="Forbidden"), 403

    db.session.execute(text("""
        UPDATE applications SET status='Cancelled' WHERE application_id = :app_id
    """), {"app_id": app_id})
    
    db.session.commit()
    log_audit("APPLICATION_CANCELLED", app_id)
    return jsonify(success=True)
