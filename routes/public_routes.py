from flask import Blueprint, request, jsonify
from models import db
from sqlalchemy import text

public_bp = Blueprint('public_bp', __name__)

# ---------------- SERVICE PRICE (Public) ----------------
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

