from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from database import get_db
from services.audit_service import log_audit

admin_bp = Blueprint('admin_bp', __name__)

# ---------- ROLE CHECK ----------
def admin_only():
    claims = get_jwt()
    return claims.get("role") == "admin"


# ---------- DASHBOARD STATS ----------
@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    if not admin_only():
        return jsonify({"success": False, "msg": "Forbidden"}), 403

    with get_db() as conn:
        total_apps = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
        active_agents = conn.execute("SELECT COUNT(*) FROM agents WHERE active=1").fetchone()[0]
        revenue = conn.execute("SELECT IFNULL(SUM(amount),0) FROM payments").fetchone()[0]

    return jsonify({
        "success": True,
        "applications": total_apps,
        "active_agents": active_agents,
        "revenue": revenue
    })


# ---------- PENDING AGENTS ----------
@admin_bp.route('/pending-agents', methods=['GET'])
@jwt_required()
def pending_agents():
    if not admin_only():
        return jsonify({"success": False, "msg": "Forbidden"}), 403

    with get_db() as conn:
        rows = conn.execute("""
            SELECT id, name, mobile, district, pincode
            FROM agents
            WHERE active = 0
        """).fetchall()

    return jsonify([dict(r) for r in rows])


# ---------- ACTIVE AGENTS ----------
@admin_bp.route('/active-agents', methods=['GET'])
@jwt_required()
def active_agents():
    if not admin_only():
        return jsonify({"success": False, "msg": "Forbidden"}), 403

    with get_db() as conn:
        rows = conn.execute("""
            SELECT id, name, mobile, district, pincode
            FROM agents
            WHERE active = 1
        """).fetchall()

    return jsonify([dict(r) for r in rows])


# ---------- APPROVE AGENT ----------
@admin_bp.route('/approve-agent/<int:agent_id>', methods=['POST'])
@jwt_required()
def approve_agent(agent_id):
    if not admin_only():
        return jsonify({"success": False, "msg": "Forbidden"}), 403

    with get_db() as conn:
        conn.execute("UPDATE agents SET active = 1 WHERE id = ?", (agent_id,))
        conn.commit()

    log_audit("AGENT_APPROVED", str(agent_id))

    return jsonify({"success": True, "message": "Agent approved"})


# ---------- DISABLE AGENT ----------
@admin_bp.route('/disable-agent/<int:agent_id>', methods=['POST'])
@jwt_required()
def disable_agent(agent_id):
    if not admin_only():
        return jsonify({"success": False, "msg": "Forbidden"}), 403

    with get_db() as conn:
        conn.execute("UPDATE agents SET active = 0 WHERE id = ?", (agent_id,))
        conn.commit()

    log_audit("AGENT_DISABLED", str(agent_id))

    return jsonify({"success": True, "message": "Agent disabled"})
# ---------- ALL APPLICATIONS ----------
@admin_bp.route('/applications', methods=['GET'])
@jwt_required()
def all_applications():
    if not admin_only():
        return jsonify(msg="Forbidden"), 403

    with get_db() as conn:
        rows = conn.execute("""
            SELECT application_id, name, mobile, service,
                   status, agent, payment_status, created_at
            FROM applications
            ORDER BY created_at DESC
        """).fetchall()

    return jsonify([dict(r) for r in rows])


# ---------- REASSIGN AGENT ----------
@admin_bp.route('/reassign/<app_id>', methods=['POST'])
@jwt_required()
def reassign(app_id):
    if not admin_only():
        return jsonify(msg="Forbidden"), 403

    new_agent = request.json.get("agent")

    with get_db() as conn:
        conn.execute(
            "UPDATE applications SET agent=? WHERE application_id=?",
            (new_agent, app_id)
        )
        conn.commit()

    log_audit("APPLICATION_REASSIGNED", app_id)
    return jsonify(success=True)


# ---------- CANCEL APPLICATION ----------
@admin_bp.route('/cancel/<app_id>', methods=['POST'])
@jwt_required()
def cancel(app_id):
    if not admin_only():
        return jsonify(msg="Forbidden"), 403

    with get_db() as conn:
        conn.execute(
            "UPDATE applications SET status='Cancelled' WHERE application_id=?",
            (app_id,)
        )
        conn.commit()

    log_audit("APPLICATION_CANCELLED", app_id)
    return jsonify(success=True)
