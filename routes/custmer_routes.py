from flask import Blueprint, request, jsonify
import uuid
from models import db
from sqlalchemy import text
from flask_jwt_extended import get_jwt_identity
from utils.security import role_required
from datetime import datetime
from utils.s3_service import upload_file

customer_bp = Blueprint("customer_bp", __name__)


# =========================================================
# 1️⃣ APPLY SERVICE
# =========================================================
@customer_bp.route("/apply-service", methods=["POST"])
@role_required("customer")
def apply_service():
    try:
        user_id = get_jwt_identity()
        app_id = "KS" + uuid.uuid4().hex[:10].upper()

        name = request.form.get("name")
        mobile = request.form.get("mobile")
        service = request.form.get("service")
        pincode = request.form.get("pincode")

        file = request.files.get("document")
        file_key = None

        # Upload to S3 if file exists
        if file:
            file_key = f"{app_id}_{file.filename}"
            upload_file(file, file_key)

        db.session.execute(text("""
            INSERT INTO applications (
                id,
                application_id,
                user_id,
                name,
                mobile,
                service,
                pincode,
                status,
                filename,
                created_at
            )
            VALUES (
                :id,
                :app_id,
                :user_id,
                :name,
                :mobile,
                :service,
                :pincode,
                'Pending Payment',
                :file,
                NOW()
            )
        """), {
            "id": str(uuid.uuid4()),
            "app_id": app_id,
            "user_id": user_id,
            "name": name,
            "mobile": mobile,
            "service": service,
            "pincode": pincode,
            "file": file_key
        })

        db.session.commit()

        return jsonify({
            "success": True,
            "application_id": app_id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================================================
# 2️⃣ GET MY APPLICATIONS
# =========================================================
@customer_bp.route("/customer/applications", methods=["GET"])
@role_required("customer")
def get_customer_applications():
    user_id = get_jwt_identity()

    try:
        apps = db.session.execute(text("""
            SELECT a.application_id,
                   a.status,
                   p.status AS payment_status,
                   a.created_at
            FROM applications a
            LEFT JOIN payments p ON p.application_id = a.application_id
            WHERE a.user_id = :user
            ORDER BY a.created_at DESC
        """), {"user": user_id}).fetchall()

        return jsonify([{
            "application_id": a.application_id,
            "status": a.status,
            "payment_status": a.payment_status,
            "created_at": a.created_at.isoformat() if a.created_at else None
        } for a in apps]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================================
# 3️⃣ RAISE TICKET
# =========================================================
@customer_bp.route("/customer/raise-ticket", methods=["POST"])
@role_required("customer")
def raise_ticket():
    user_id = get_jwt_identity()
    data = request.get_json()

    try:
        db.session.execute(text("""
            INSERT INTO tickets (
                id,
                application_id,
                user_id,
                category,
                description,
                priority,
                status,
                created_at
            )
            VALUES (
                :id,
                :application_id,
                :user_id,
                :category,
                :description,
                :priority,
                'Open',
                NOW()
            )
        """), {
            "id": str(uuid.uuid4()),
            "application_id": data["application_id"],
            "user_id": user_id,
            "category": data["category"],
            "description": data["description"],
            "priority": data.get("priority", "normal")
        })

        db.session.commit()

        return jsonify({"message": "Ticket submitted successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# =========================================================
# 4️⃣ MY TICKETS
# =========================================================
@customer_bp.route("/customer/my-tickets", methods=["GET"])
@role_required("customer")
def get_my_tickets():
    user_id = get_jwt_identity()

    try:
        tickets = db.session.execute(text("""
            SELECT id,
                   application_id,
                   category,
                   status,
                   priority,
                   created_at
            FROM tickets
            WHERE user_id = :user
            ORDER BY created_at DESC
        """), {"user": user_id}).fetchall()

        return jsonify([{
            "id": str(t.id),
            "application_id": t.application_id,
            "category": t.category,
            "status": t.status,
            "priority": t.priority,
            "created_at": t.created_at.isoformat() if t.created_at else None
        } for t in tickets]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
