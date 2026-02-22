from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import text
from models import db
from datetime import datetime

# Initialize Blueprint
customer_bp = Blueprint('customer_bp', __name__)

# ---------------- RAISE TICKET ----------------
@customer_bp.route("/api/customer/raise-ticket", methods=["POST"])
@jwt_required()
def raise_ticket():
    user_id = get_jwt_identity()
    data = request.json

    # Basic validation for required fields
    if not data or "application_id" not in data or "category" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        db.session.execute(text("""
            INSERT INTO tickets 
            (application_id, user_id, category, description, priority, created_at)
            VALUES (:app, :user, :category, :desc, :priority, :now)
        """), {
            "app": data["application_id"],
            "user": user_id,
            "category": data["category"],
            "desc": data["description"],
            "priority": data.get("priority", "normal"),
            "now": datetime.utcnow()
        })

        db.session.commit()
        return jsonify({"message": "Ticket submitted for review"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to submit ticket", "details": str(e)}), 500

# ---------------- GET CUSTOMER TICKETS ----------------
@customer_bp.route("/api/customer/my-tickets", methods=["GET"])
@jwt_required()
def get_my_tickets():
    user_id = get_jwt_identity()
    
    result = db.session.execute(text("""
        SELECT ticket_id, application_id, category, status, priority, created_at 
        FROM tickets 
        WHERE user_id = :user
        ORDER BY created_at DESC
    """), {"user": user_id})
    
    tickets = [dict(row) for row in result]
    return jsonify(tickets)
