from flask import Blueprint, request, jsonify
import uuid
import os
from models import db
from sqlalchemy import text
from flask_jwt_extended import get_jwt_identity
from utils.security import role_required

public_bp = Blueprint('public_bp', __name__)

# ---------------- SERVICE PRICE (Public) ----------------
# This remains accessible to everyone so they can check prices before logging in
@public_bp.route("/api/service-price", methods=["GET"])
def get_service_price():
    service_name = request.args.get("service")

    try:
        row = db.session.execute(text("""
            SELECT price FROM services WHERE service_name = :name
        """), {"name": service_name}).fetchone()

        # Fallback to 500 if service not found
        price = row.price if row else 500
        return jsonify({"price": price}), 200
    except Exception as e:
        return jsonify({"error": "Could not fetch price", "details": str(e)}), 500


# ---------------- APPLY SERVICE (Customer Protected) ----------------
@public_bp.route('/api/apply-service', methods=['POST'])
@role_required("customer")
def apply():
    try:
        # Get the authenticated user's ID from the JWT
        user_id = get_jwt_identity()
        
        # Generate a unique application ID
        app_id = "KS" + uuid.uuid4().hex[:10].upper()

        # Extracting data from Form-Data (useful for file uploads)
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

        # Insert application into database
        db.session.execute(text("""
            INSERT INTO applications (
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
                :app_id, 
                :u_id, 
                :name, 
                :mobile, 
                :service, 
                :pin, 
                'Pending Payment', 
                :file, 
                NOW()
            )
        """), {
            "app_id": app_id,
            "u_id": user_id,
            "name": name,
            "mobile": mobile,
            "service": service,
            "pin": pincode,
            "file": file_path
        })
        
        db.session.commit()

        return jsonify({
            "success": True,
            "application_id": app_id,
            "message": "Application submitted successfully"
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Apply Error: {e}")
        return jsonify({"success": False, "msg": "Database Error or Invalid Input"}), 500

# ---------------- GET MY APPLICATIONS (Customer Protected) ----------------
@public_bp.route('/api/my-applications', methods=['GET'])
@role_required("customer")
def get_my_applications():
    user_id = get_jwt_identity()
    
    try:
        apps = db.session.execute(text("""
            SELECT application_id, service, status, created_at 
            FROM applications 
            WHERE user_id = :u_id 
            ORDER BY created_at DESC
        """), {"u_id": user_id}).fetchall()

        result = []
        for a in apps:
            result.append({
                "id": a.application_id,
                "service": a.service,
                "status": a.status,
                "date": a.created_at.strftime("%Y-%m-%d")
            })
            
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

