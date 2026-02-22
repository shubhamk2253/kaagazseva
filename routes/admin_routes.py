from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from sqlalchemy import text
from utils.security import role_required
import uuid
from datetime import datetime

admin_bp = Blueprint('admin_bp', __name__)

# --- 1. FOUNDER DASHBOARD & ANALYTICS ---
@admin_bp.route("/api/admin/dashboard", methods=["GET"])
@role_required("founder")
def founder_dashboard():
    try:
        # 1️⃣ Revenue & Commission Summary
        # Using COALESCE to ensure 0 is returned instead of None
        stats = db.session.execute(text("""
            SELECT 
                (SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status='paid') as total_revenue,
                (SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status='refunded') as total_refunds,
                (SELECT COALESCE(SUM(balance), 0) FROM agent_wallets) as pending_payouts,
                (SELECT COUNT(*) FROM applications) as total_apps,
                (SELECT COUNT(*) FROM agents WHERE is_verified=TRUE) as active_agents
            """)).fetchone()

        # 2️⃣ Refund Ratio Calculation
        refunded_count = db.session.execute(text("""
            SELECT COUNT(*) FROM tickets 
            WHERE category='Refund' AND status='Resolved'
        """)).scalar() or 0
        
        refund_ratio = (refunded_count / stats.total_apps * 100) if stats.total_apps > 0 else 0

        # 3️⃣ State Performance (Market Share)
        state_data = db.session.execute(text("""
            SELECT state_id, COUNT(*) as total
            FROM applications
            GROUP BY state_id
            ORDER BY total DESC
        """)).fetchall()

        # 4️⃣ Top Performing Agents
        agent_data = db.session.execute(text("""
            SELECT u.full_name, COUNT(a.id) as completed
            FROM applications a
            JOIN users u ON a.agent_id = u.id
            WHERE a.status='Completed'
            GROUP BY u.full_name
            ORDER BY completed DESC
            LIMIT 5
        """)).fetchall()

        return jsonify({
            "summary": {
                "total_revenue": float(stats.total_revenue),
                "total_refunds": float(stats.total_refunds),
                "net_revenue": float(stats.total_revenue - stats.total_refunds),
                "pending_payouts": float(stats.pending_payouts),
                "active_agents": stats.active_agents,
                "refund_ratio_percent": round(refund_ratio, 2)
            },
            "state_performance": [{"state_id": row.state_id, "count": row.total} for row in state_data],
            "top_agents": [{"name": row.full_name, "completed": row.completed} for row in agent_data]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- 2. AGENT MANAGEMENT (APPROVE/REJECT) ---
@admin_bp.route("/api/admin/pending-agents", methods=["GET"])
@role_required("founder") # Logic inside handles state_admin escalation
def get_pending_agents():
    user_id = get_jwt_identity()
    user = db.session.execute(text("SELECT role FROM users WHERE id = :id"), {"id": user_id}).fetchone()

    # Base Query
    query_str = "SELECT id, full_name, mobile, email, state_id, created_at FROM agent_registrations WHERE status = 'pending'"
    params = {}

    if user.role == "state_admin":
        admin_data = db.session.execute(text("SELECT state_id FROM agents WHERE id = :id"), {"id": user_id}).fetchone()
        if not admin_data: return jsonify({"error": "Unauthorized"}), 403
        query_str += " AND state_id = :state_id"
        params["state_id"] = admin_data.state_id

    agents = db.session.execute(text(query_str + " ORDER BY created_at DESC"), params).fetchall()
    return jsonify([dict(a._mapping) for a in agents])

@admin_bp.route("/api/admin/approve-agent/<registration_id>", methods=["POST"])
@role_required("founder")
def approve_agent(registration_id):
    reg = db.session.execute(text("SELECT * FROM agent_registrations WHERE id = :id"), {"id": registration_id}).fetchone()
    if not reg: return jsonify({"error": "Not found"}), 404

    try:
        new_agent_id = str(uuid.uuid4())
        # Atomic Transaction: Create User -> Profile -> Wallet -> Update Reg
        db.session.execute(text("INSERT INTO users (id, full_name, mobile, email, role) VALUES (:id, :n, :m, :e, 'agent')"),
                           {"id": new_agent_id, "n": reg.full_name, "m": reg.mobile, "e": reg.email})
        
        db.session.execute(text("INSERT INTO agents (id, state_id, district_id, is_verified) VALUES (:id, :s, :d, TRUE)"),
                           {"id": new_agent_id, "s": reg.state_id, "d": reg.district_id})
        
        db.session.execute(text("INSERT INTO agent_wallets (agent_id, balance) VALUES (:id, 0)"), {"id": new_agent_id})
        
        db.session.execute(text("UPDATE agent_registrations SET status='approved' WHERE id=:id"), {"id": registration_id})
        
        db.session.commit()
        return jsonify({"message": "Agent approved", "agent_id": new_agent_id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# --- 3. PAYOUTS ---
@admin_bp.route("/api/admin/payout/<agent_id>", methods=["POST"])
@role_required("founder")
def payout_agent(agent_id):
    wallet = db.session.execute(text("SELECT balance FROM agent_wallets WHERE agent_id = :id"), {"id": agent_id}).fetchone()

    if not wallet or wallet.balance <= 0:
        return jsonify({"message": "Insufficient balance"}), 400

    try:
        amount = wallet.balance
        db.session.execute(text("UPDATE agent_wallets SET balance = 0 WHERE agent_id = :id"), {"id": agent_id})
        # Record keeping
        db.session.execute(text("INSERT INTO payout_history (agent_id, amount, created_at) VALUES (:id, :amt, NOW())"),
                           {"id": agent_id, "amt": amount})
        db.session.commit()
        return jsonify({"message": f"Payout of {amount} successful"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# --- 4. TICKET RESOLUTION ---
@admin_bp.route("/api/admin/open-tickets", methods=["GET"])
@role_required("founder")
def view_open_tickets():
    tickets = db.session.execute(text("""
        SELECT t.id, t.application_id, t.category, t.priority, t.description, u.full_name
        FROM tickets t JOIN users u ON t.user_id = u.id
        WHERE t.status != 'Resolved' ORDER BY t.created_at DESC
    """)).fetchall()
    return jsonify([dict(t._mapping) for t in tickets])

@admin_bp.route("/api/admin/resolve-ticket/<ticket_id>", methods=["POST"])
@role_required("founder")
def resolve_ticket(ticket_id):
    data = request.json
    res_note = data.get("resolution_note")
    is_refund = data.get("approve_refund", False)

    ticket = db.session.execute(text("SELECT application_id FROM tickets WHERE id=:id"), {"id": ticket_id}).fetchone()
    if not ticket: return jsonify({"error": "Ticket not found"}), 404

    try:
        if is_refund:
            db.session.execute(text("UPDATE payments SET status='refunded' WHERE application_id=:app"), 
                               {"app": ticket.application_id})

        db.session.execute(text("""
            UPDATE tickets SET resolution_note=:note, status='Resolved', updated_at=NOW() WHERE id=:id
        """), {"note": res_note, "id": ticket_id})

        db.session.commit()
        return jsonify({"message": "Ticket closed"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500        db.session.rollback()
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


# --- VIEW OPEN TICKETS (FOUNDER ONLY) ---
@admin_bp.route("/api/admin/open-tickets", methods=["GET"])
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

    result = []
    for t in tickets:
        result.append({
            "id": str(t.id),
            "application_id": str(t.application_id),
            "category": t.category,
            "priority": t.priority,
            "description": t.description,
            "user": t.full_name
        })

    return jsonify(result)


# --- RESOLVE TICKET (FOUNDER ONLY) ---
@admin_bp.route("/api/admin/resolve-ticket/<ticket_id>", methods=["POST"])
@role_required("founder")
def resolve_ticket(ticket_id):
    admin_id = get_jwt_identity()
    data = request.json
    resolution_note = data.get("resolution_note")

    ticket = db.session.execute(text("""
        SELECT * FROM tickets WHERE id=:id
    """), {"id": ticket_id}).fetchone()

    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    # Refund logic based on category
    if ticket.category == "agent_mistake":
        refund_allowed = True
    elif ticket.category == "platform_failure":
        refund_allowed = True
    else:
        refund_allowed = False

    try:
        if refund_allowed:
            # Mark payment refunded
            db.session.execute(text("""
                UPDATE payments 
                SET status='refunded' 
                WHERE application_id=:app
            """), {"app": ticket.application_id})

        db.session.execute(text("""
            UPDATE tickets
            SET resolution_note=:note,
                resolved_by=:admin,
                updated_at=NOW()
            WHERE id=:id
        """), {
            "note": resolution_note,
            "admin": admin_id,
            "id": ticket_id
        })

        db.session.commit()
        return jsonify({"message": "Ticket resolved", "refund": refund_allowed}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Resolution failed", "details": str(e)}), 500

