from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import text
from models import db
from utils.security import role_required
import uuid

admin_bp = Blueprint("admin_bp", __name__)


# =========================================================
# 1️⃣ FOUNDER CONTROL TOWER (Elite Analytics)
# =========================================================
@admin_bp.route("/founder/control-tower", methods=["GET"])
@role_required("founder")
def founder_control_tower():
    try:
        stats = db.session.execute(text("""
            SELECT 
                (SELECT COALESCE(SUM(amount),0) FROM payments WHERE status='Paid') as total_rev,
                (SELECT COALESCE(SUM(amount),0) FROM payments WHERE status='Paid' AND DATE(created_at)=CURRENT_DATE) as today_rev,
                (SELECT COALESCE(SUM(platform_commission),0) FROM applications WHERE status='Completed') as total_prof,
                (SELECT COALESCE(SUM(balance),0) FROM agent_wallets) as pend_payout,
                (SELECT COUNT(*) FROM applications) as total_apps,
                (SELECT COUNT(*) FROM tickets WHERE category='Refund' AND status='Resolved') as ref_apps
        """)).fetchone()

        refund_ratio = (stats.ref_apps / stats.total_apps * 100) if stats.total_apps else 0
        risk_status = "HIGH REFUND RISK" if refund_ratio > 15 else "STABLE"

        state_data = db.session.execute(text("""
            SELECT state_id, COUNT(*) as total 
            FROM applications 
            GROUP BY state_id 
            ORDER BY total DESC
        """)).fetchall()

        agent_data = db.session.execute(text("""
            SELECT u.full_name, COUNT(a.id) as completed
            FROM applications a
            JOIN users u ON a.agent_id = u.id
            WHERE a.status='Completed'
            GROUP BY u.full_name
            ORDER BY completed DESC
            LIMIT 10
        """)).fetchall()

        return jsonify({
            "metrics": {
                "total_revenue": float(stats.total_rev),
                "today_revenue": float(stats.today_rev),
                "total_profit": float(stats.total_prof),
                "pending_payouts": float(stats.pend_payout),
                "refund_ratio_percent": round(refund_ratio, 2),
                "total_applications": stats.total_apps
            },
            "state_performance": [
                {"state": r.state_id, "applications": r.total} for r in state_data
            ],
            "top_agents": [
                {"agent": r.full_name, "completed_orders": r.completed} for r in agent_data
            ],
            "risk_status": risk_status
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================================
# 2️⃣ GET PENDING AGENTS (Founder + State Admin)
# =========================================================
@admin_bp.route("/admin/pending-agents", methods=["GET"])
@role_required("founder")
def get_pending_agents():
    user_id = get_jwt_identity()

    user = db.session.execute(
        text("SELECT role FROM users WHERE id = :id"),
        {"id": user_id}
    ).fetchone()

    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.role == "founder":
        query = text("""
            SELECT id, full_name, mobile, email, state_id, created_at
            FROM agent_registrations
            WHERE status='pending'
            ORDER BY created_at DESC
        """)
        agents = db.session.execute(query).fetchall()

    elif user.role == "state_admin":
        admin_state = db.session.execute(
            text("SELECT state_id FROM agents WHERE id=:id"),
            {"id": user_id}
        ).fetchone()

        if not admin_state:
            return jsonify({"error": "Unauthorized"}), 403

        query = text("""
            SELECT id, full_name, mobile, email, state_id, created_at
            FROM agent_registrations
            WHERE status='pending' AND state_id=:state
            ORDER BY created_at DESC
        """)
        agents = db.session.execute(query, {"state": admin_state.state_id}).fetchall()

    else:
        return jsonify({"error": "Unauthorized role"}), 403

    return jsonify([dict(a._mapping) for a in agents])


# =========================================================
# 3️⃣ APPROVE AGENT
# =========================================================
@admin_bp.route("/admin/approve-agent/<registration_id>", methods=["POST"])
@role_required("founder")
def approve_agent(registration_id):

    reg = db.session.execute(
        text("SELECT * FROM agent_registrations WHERE id=:id"),
        {"id": registration_id}
    ).fetchone()

    if not reg:
        return jsonify({"error": "Application not found"}), 404

    try:
        new_agent_id = str(uuid.uuid4())

        db.session.execute(text("""
            INSERT INTO users (id, full_name, mobile, email, role)
            VALUES (:id, :name, :mobile, :email, 'agent')
        """), {
            "id": new_agent_id,
            "name": reg.full_name,
            "mobile": reg.mobile,
            "email": reg.email
        })

        db.session.execute(text("""
            INSERT INTO agents (id, state_id, district_id, is_verified)
            VALUES (:id, :state, :district, TRUE)
        """), {
            "id": new_agent_id,
            "state": reg.state_id,
            "district": reg.district_id
        })

        db.session.execute(text("""
            INSERT INTO agent_wallets (agent_id, balance)
            VALUES (:id, 0)
        """), {"id": new_agent_id})

        db.session.execute(text("""
            UPDATE agent_registrations
            SET status='approved'
            WHERE id=:id
        """), {"id": registration_id})

        db.session.commit()

        return jsonify({
            "message": "Agent approved successfully",
            "agent_id": new_agent_id
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# =========================================================
# 4️⃣ REJECT AGENT
# =========================================================
@admin_bp.route("/admin/reject-agent/<registration_id>", methods=["POST"])
@role_required("founder")
def reject_agent(registration_id):
    db.session.execute(text("""
        UPDATE agent_registrations
        SET status='rejected'
        WHERE id=:id
    """), {"id": registration_id})
    db.session.commit()

    return jsonify({"message": "Agent rejected"}), 200


# =========================================================
# 5️⃣ VIEW OPEN TICKETS
# =========================================================
@admin_bp.route("/admin/open-tickets", methods=["GET"])
@role_required("founder")
def view_open_tickets():
    tickets = db.session.execute(text("""
        SELECT t.id, t.application_id, t.category, t.priority,
               t.description, u.full_name
        FROM tickets t
        JOIN users u ON t.user_id = u.id
        WHERE t.resolution_note IS NULL
        ORDER BY t.created_at DESC
    """)).fetchall()

    return jsonify([dict(t._mapping) for t in tickets])


# =========================================================
# 6️⃣ RESOLVE TICKET
# =========================================================
@admin_bp.route("/admin/resolve-ticket/<ticket_id>", methods=["POST"])
@role_required("founder")
def resolve_ticket(ticket_id):
    data = request.json
    resolution_note = data.get("resolution_note")

    ticket = db.session.execute(
        text("SELECT * FROM tickets WHERE id=:id"),
        {"id": ticket_id}
    ).fetchone()

    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    try:
        refund_allowed = ticket.category in ["agent_mistake", "platform_failure"]

        if refund_allowed:
            db.session.execute(text("""
                UPDATE payments
                SET status='refunded'
                WHERE application_id=:app
            """), {"app": ticket.application_id})

        db.session.execute(text("""
            UPDATE tickets
            SET resolution_note=:note,
                updated_at=NOW()
            WHERE id=:id
        """), {
            "note": resolution_note,
            "id": ticket_id
        })

        db.session.commit()

        return jsonify({
            "message": "Ticket resolved",
            "refund_processed": refund_allowed
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
