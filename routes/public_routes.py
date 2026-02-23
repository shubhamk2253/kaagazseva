from flask import Blueprint, request, jsonify
from models import db
from sqlalchemy import text

public_bp = Blueprint("public_bp", __name__)


# =========================================================
# 1️⃣ GET SERVICE PRICE (Legacy / Fallback)
# =========================================================
@public_bp.route("/service-price", methods=["GET"])
def get_service_price():
    service_name = request.args.get("service")

    if not service_name:
        return jsonify({"error": "Service name required"}), 400

    try:
        row = db.session.execute(text("""
            SELECT price
            FROM services
            WHERE service_name = :name
        """), {"name": service_name}).fetchone()

        price = float(row.price) if row else 500.0  # fallback default

        return jsonify({"price": price}), 200

    except Exception as e:
        return jsonify({
            "error": "Could not fetch price",
            "details": str(e)
        }), 500


# =========================================================
# 2️⃣ GET SERVICES BY STATE (Dynamic Pricing)
# =========================================================
@public_bp.route("/services/<state_id>", methods=["GET"])
def get_services_by_state(state_id):
    try:
        services = db.session.execute(text("""
            SELECT id,
                   service_name,
                   final_price,
                   government_fee,
                   service_fee,
                   required_documents,
                   processing_time
            FROM state_services
            WHERE state_id = :state
            AND is_active = TRUE
        """), {"state": state_id}).fetchall()

        result = [{
            "id": str(s.id),
            "service_name": s.service_name,
            "final_price": float(s.final_price),
            "government_fee": float(s.government_fee),
            "service_fee": float(s.service_fee),
            "required_documents": s.required_documents,
            "processing_time": s.processing_time
        } for s in services]

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "error": "Failed to fetch state services",
            "details": str(e)
        }), 500


# =========================================================
# 3️⃣ GET ALL STATES
# =========================================================
@public_bp.route("/states", methods=["GET"])
def get_states():
    try:
        states = db.session.execute(text("""
            SELECT id, name
            FROM states
            ORDER BY name
        """)).fetchall()

        return jsonify([
            {"id": str(s.id), "name": s.name}
            for s in states
        ]), 200

    except Exception as e:
        return jsonify({
            "error": "Failed to fetch states",
            "details": str(e)
        }), 500
