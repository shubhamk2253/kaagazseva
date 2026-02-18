from flask import Blueprint, request, jsonify
import uuid
import os
from database import get_db

public_bp = Blueprint('public_bp', __name__)

# ---------------- SERVICE PRICE ----------------
@public_bp.route("/service-price")
def get_service_price():
    service = request.args.get("service")

    with get_db() as conn:
        row = conn.execute(
            "SELECT price FROM services WHERE service_name=?",
            (service,)
        ).fetchone()

    price = row["price"] if row else 500
    return jsonify({"price": price})


# ---------------- APPLY SERVICE ----------------
@public_bp.route('/apply-service', methods=['POST'])
def apply():
    try:
        app_id = "KS" + uuid.uuid4().hex[:10].upper()

        name = request.form.get('name')
        mobile = request.form.get('mobile')
        service = request.form.get('service')
        pincode = request.form.get('pincode')

        file = request.files.get('document')
        file_path = ""

        if file:
            os.makedirs('uploads', exist_ok=True)
            filename = f"{app_id}_{file.filename}"
            file_path = os.path.join('uploads', filename)
            file.save(file_path)

        with get_db() as conn:
            conn.execute("""
                INSERT INTO applications(
                    application_id, name, mobile, service,
                    pincode, status, filename
                )
                VALUES(?,?,?,?,?,?,?)
            """, (
                app_id, name, mobile, service,
                pincode, "Pending Payment", file_path
            ))
            conn.commit()

        return jsonify({
            "success": True,
            "application_id": app_id
        })

    except Exception as e:
        print("Apply Error:", e)
        return jsonify({"success": False, "msg": "Database Error"}), 500
