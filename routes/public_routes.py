from flask import Blueprint, request, jsonify
from models import db
from sqlalchemy import text

public_bp = Blueprint('public_bp', __name__)

# ---------------- GET SERVICE PRICE (Legacy/Fallback) ----------------
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


# ---------------- GET SERVICES BY STATE (Dynamic Pricing) ----------------
@public_bp.route("/api/services/<state_id>", methods=["GET"])
def get_services_by_state(state_id):
    try:
        services = db.session.execute(text("""
            SELECT id, service_name, final_price, 
                   government_fee, service_fee, 
                   required_documents, processing_time
            FROM state_services 
            WHERE state_id = :state 
            AND is_active = TRUE
        """), {"state": state_id}).fetchall()

        result = []
        for s in services:
            result.append({
                "id": str(s.id),
                "service_name": s.service_name,
                "final_price": float(s.final_price),
                "government_fee": float(s.government_fee),
                "service_fee": float(s.service_fee),
                "documents": s.required_documents, # Assuming this is a text or JSON field
                "processing_time": s.processing_time
            })

        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({"error": "Failed to fetch state services", "details": str(e)}), 500

# ---------------- GET ALL STATES (For Dropdown) ----------------
@public_bp.route("/api/states", methods=["GET"])
def get_states():
    try:
        states = db.session.execute(text("SELECT id, name FROM states ORDER BY name")).fetchall()
        return jsonify([{"id": s.id, "name": s.name} for s in states]), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch states"}), 500
