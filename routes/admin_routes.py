from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from sqlalchemy import text

admin_bp = Blueprint('admin_bp', __name__)

# --- GET PENDING AGENTS ---
@admin_bp.route("/api/admin/pending-agents", methods=["GET"])
@jwt_required()
def get_pending_agents():
    user_id = get_jwt_identity()

    # Fetch the current user's role
    user = db.session.execute(text("""
        SELECT role FROM users WHERE id = :id
    """), {"id": user_id}).fetchone()

    if not user:
        return jsonify({"error": "Unauthorized"}), 403

    # LOGIC FOR FOUNDER: See all pending applications nationally
    if user.role == "founder":
        agents = db.session.execute(text("""
            SELECT ar.id, ar.full_name, ar.mobile, ar.email, ar.state_id, ar.created_at
            FROM agent_registrations ar
            WHERE ar.status = 'pending'
            ORDER BY ar.created_at DESC
        """)).fetchall()

    # LOGIC FOR STATE ADMIN: See only own state's pending applications
    elif user.role == "state_admin":
        # Get the state_id assigned to this admin from the agents table
        admin_data = db.session.execute(text("""
            SELECT state_id FROM agents WHERE id = :id
        """), {"id": user_id}).fetchone()

        if not admin_data:
            return jsonify({"error": "Admin state record not found"}), 404

        agents = db.session.execute(text("""
            SELECT ar.id, ar.full_name, ar.mobile, ar.email, ar.state_id, ar.created_at
            FROM agent_registrations ar
            WHERE ar.status = 'pending'
            AND ar.state_id = :state_id
            ORDER BY ar.created_at DESC
        """), {"state_id": admin_data.state_id}).fetchall()

    else:
        return jsonify({"error": "Unauthorized access level"}), 403

    # Format result for JSON response
    result = []
    for a in agents:
        result.append({
            "id": str(a.id),
            "full_name": a.full_name,
            "mobile": a.mobile,
            "email": a.email,
            "state_id": a.state_id,
            "created_at": a.created_at
        })

    return jsonify(result)


# --- APPROVE AGENT ---
@admin_bp.route("/api/admin/approve-agent/<agent_id>", methods=["POST"])
@jwt_required()
def approve_agent(agent_id):
    user_id = get_jwt_identity()

    # Fetch the current admin's role
    admin = db.session.execute(text("""
        SELECT role FROM users WHERE id = :id
    """), {"id": user_id}).fetchone()

    if not admin:
        return jsonify({"error": "Unauthorized"}), 403

    # Fetch the target agent application
    agent_app = db.session.execute(text("""
        SELECT * FROM agent_registrations WHERE id = :id
    """), {"id": agent_id}).fetchone()

    if not agent_app:
        return jsonify({"error": "Application not found"}), 404

    # SECURITY CHECK: If state admin, restrict approval to their own state only
    if admin.role == "state_admin":
        admin_state = db.session.execute(text("""
            SELECT state_id FROM agents WHERE id = :id
        """), {"id": user_id}).fetchone()

        if not admin_state or agent_app.state_id != admin_state.state_id:
            return jsonify({"error": "Unauthorized: This agent belongs to a different state"}), 403

    # Only Founders and Authorized State Admins can reach this point
    elif admin.role != "founder":
        return jsonify({"error": "Unauthorized"}), 403

    try:
        # 1. Create the user entry and get back the generated UUID
        new_user = db.session.execute(text("""
            INSERT INTO users (id, full_name, mobile, email, role)
            VALUES (gen_random_uuid(), :name, :mobile, :email, 'agent')
            RETURNING id
        """), {
            "name": agent_app.full_name,
            "mobile": agent_app.mobile,
            "email": agent_app.email
        }).fetchone()

        new_user_id = new_user.id

        # 2. Create the agent profile entry
        db.session.execute(text("""
            INSERT INTO agents (id, state_id, district_id, is_verified)
            VALUES (:id, :state, :district, TRUE)
        """), {
            "id": new_user_id,
            "state": agent_app.state_id,
            "district": agent_app.district_id
        })

        # 3. Mark the registration as approved
        db.session.execute(text("""
            UPDATE agent_registrations
            SET status='approved'
            WHERE id=:id
        """), {"id": agent_id})

        db.session.commit()
        return jsonify({
            "message": f"Agent {agent_app.full_name} approved successfully", 
            "user_id": str(new_user_id)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500


# --- REJECT AGENT ---
@admin_bp.route("/api/admin/reject-agent/<agent_id>", methods=["POST"])
@jwt_required()
def reject_agent(agent_id):
    user_id = get_jwt_identity()
    
    # Check if user is admin/founder
    user_check = db.session.execute(text("SELECT role FROM users WHERE id = :id"), {"id": user_id}).fetchone()
    if not user_check or user_check.role not in ['founder', 'state_admin']:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.execute(text("""
        UPDATE agent_registrations 
        SET status='rejected' 
        WHERE id=:id
    """), {"id": agent_id})
    
    db.session.commit()
    return jsonify({"message": "Agent application rejected"}), 200
