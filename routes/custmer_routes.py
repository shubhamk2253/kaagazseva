from flask import Blueprint, request, jsonify
import uuid
import os
from models import db
from sqlalchemy import text
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.security import role_required
from datetime import datetime

customer_bp = Blueprint('customer_bp', __name__)

# ---------------- APPLY SERVICE ----------------
@customer_bp.route('/api/apply-service', methods=['POST'])
@role_required("customer")
def apply():
    try:
        user_id = get_jwt_identity()
        app_id = "KS" + uuid.uuid4().hex[:10].upper()

        name = request.form.get('name')
        mobile = request.form.get('mobile')
        service = request.form.get('service')
        pincode = request.form.get('pincode')

        # Handle File Upload
        file = request.files.get('document')
        file_path = ""

        if file:
            upload_folder = 'uploads'
            os.makedirs(upload_folder, exist_ok=True)
            filename = f"{app_id}_{file.filename}"
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

        db.session.execute(text("""
            INSERT INTO applications (
                application_id, user_id, name, mobile, service, pincode, 
                status, filename, created_at
            )
            VALUES (
                :app_id, :u_id, :name, :mobile, :service, :pin, 
                'Pending Payment', :file, NOW()
            )
        """), {
            "app_id": app_id, "u_id": user_id, "name": name, 
            "mobile": mobile, "service": service, "pin": pincode, "file": file_path
        })
        
        db.session.commit()
        return jsonify({"success": True, "application_id": app_id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ---------------- GET APPLICATIONS ----------------
@customer_bp.route("/api/customer/applications", methods=["GET"])
@role_required("customer")
def get_customer_applications():
    user_id = get_jwt_identity()
    try:
        apps = db.session.execute(text("""
            SELECT a.id, ss.service_name, a.status, p.status AS payment_status, a.mode, a.created_at
            FROM applications a
            JOIN state_services ss ON a.state_service_id = ss.id
            LEFT JOIN payments p ON p.application_id = a.id
            WHERE a.user_id = :user
            ORDER BY a.created_at DESC
        """), {"user": user_id}).fetchall()

        return jsonify([{
            "id": str(a.id),
            "service_name": a.service_name,
            "status": a.status,
            "payment_status": a.payment_status,
            "mode": a.mode,
            "created_at": a.created_at.isoformat() if a.created_at else None
        } for a in apps]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- RAISE TICKET ----------------
@customer_bp.route("/api/customer/raise-ticket", methods=["POST"])
@role_required("customer")
def raise_ticket():
    user_id = get_jwt_identity()
    data = request.json
    try:
        db.session.execute(text("""
            INSERT INTO tickets (application_id, user_id, category, description, priority, created_at)
            VALUES (:app, :user, :category, :desc, :priority, :now)
        """), {
            "app": data["application_id"], "user": user_id, "category": data["category"],
            "desc": data["description"], "priority": data.get("priority", "normal"), "now": datetime.utcnow()
        })
        db.session.commit()
        return jsonify({"message": "Ticket submitted"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ---------------- MY TICKETS ----------------
@customer_bp.route("/api/customer/my-tickets", methods=["GET"])
@role_required("customer")
def get_my_tickets():
    user_id = get_jwt_identity()
    try:
        result = db.session.execute(text("""
            SELECT id, application_id, category, status, priority, created_at 
            FROM tickets WHERE user_id = :user ORDER BY created_at DESC
        """), {"user": user_id}).fetchall()
        
        return jsonify([{
            "id": row.id, "application_id": row.application_id, "category": row.category,
            "status": row.status, "priority": row.priority, "created_at": row.created_at
        } for row in result]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
