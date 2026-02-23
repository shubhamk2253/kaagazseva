from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import text
from models import db
from datetime import datetime, timedelta
import random
import uuid

auth_bp = Blueprint("auth_bp", __name__)


# =========================================================
# 1️⃣ SEND OTP
# =========================================================
@auth_bp.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    mobile = data.get("mobile")
    login_type = data.get("type")  # agent | customer

    if not mobile or login_type not in ["agent", "customer"]:
        return jsonify({"error": "Invalid request"}), 400

    try:
        # Check if user exists
        user = db.session.execute(text("""
            SELECT id, role FROM users WHERE mobile = :mobile
        """), {"mobile": mobile}).fetchone()

        # ---------------- Agent Login Rules ----------------
        if login_type == "agent":
            if not user or user.role != "agent":
                return jsonify({"error": "Agent not registered"}), 403

            agent_status = db.session.execute(text("""
                SELECT is_verified FROM agents WHERE id = :id
            """), {"id": user.id}).fetchone()

            if not agent_status or not agent_status.is_verified:
                return jsonify({"error": "Agent not verified"}), 403

        # ---------------- Customer Auto Registration ----------------
        if login_type == "customer" and not user:
            db.session.execute(text("""
                INSERT INTO users (id, mobile, role, created_at)
                VALUES (:id, :mobile, 'customer', NOW())
            """), {
                "id": str(uuid.uuid4()),
                "mobile": mobile
            })
            db.session.commit()

        # Generate OTP
        otp = str(random.randint(100000, 999999))
        expires = datetime.utcnow() + timedelta(minutes=5)

        db.session.execute(text("""
            INSERT INTO otp_sessions
            (id, mobile, otp_code, expires_at, is_used, created_at)
            VALUES (:id, :mobile, :otp, :expires, FALSE, NOW())
        """), {
            "id": str(uuid.uuid4()),
            "mobile": mobile,
            "otp": otp,
            "expires": expires
        })

        db.session.commit()

        # TODO: Integrate SMS provider
        print(f"DEBUG OTP for {mobile}: {otp}")

        return jsonify({"message": "OTP sent successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# =========================================================
# 2️⃣ VERIFY OTP
# =========================================================
@auth_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    mobile = data.get("mobile")
    otp = data.get("otp")

    if not mobile or not otp:
        return jsonify({"error": "Invalid request"}), 400

    try:
        record = db.session.execute(text("""
            SELECT id FROM otp_sessions
            WHERE mobile = :mobile
            AND otp_code = :otp
            AND is_used = FALSE
            AND expires_at > NOW()
            ORDER BY created_at DESC
            LIMIT 1
        """), {
            "mobile": mobile,
            "otp": otp
        }).fetchone()

        if not record:
            return jsonify({"error": "Invalid or expired OTP"}), 400

        # Mark OTP as used
        db.session.execute(text("""
            UPDATE otp_sessions
            SET is_used = TRUE
            WHERE id = :id
        """), {"id": record.id})

        # Fetch user
        user = db.session.execute(text("""
            SELECT id, role FROM users WHERE mobile = :mobile
        """), {"mobile": mobile}).fetchone()

        if not user:
            return jsonify({"error": "User not found"}), 404

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role}
        )

        db.session.commit()

        return jsonify({
            "access_token": token,
            "role": user.role,
            "user_id": str(user.id)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# =========================================================
# 3️⃣ FOUNDER LOGIN (Email + Password)
# =========================================================
@auth_bp.route("/auth/admin-login", methods=["POST"])
def admin_login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    try:
        user = db.session.execute(text("""
            SELECT id, password_hash, role
            FROM users
            WHERE email = :email
        """), {"email": username}).fetchone()

        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        if not user.password_hash or not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid credentials"}), 401

        if user.role != "founder":
            return jsonify({"error": "Unauthorized"}), 403

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role}
        )

        return jsonify({"access_token": token}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================================
# 4️⃣ CHANGE PASSWORD
# =========================================================
@auth_bp.route("/auth/change-password", methods=["POST"])
@jwt_required()
def change_password():
    data = request.get_json()
    user_id = get_jwt_identity()

    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    new_password = data.get("new_password")

    if not new_password:
        return jsonify({"error": "Password required"}), 400

    try:
        new_hash = generate_password_hash(new_password)

        db.session.execute(text("""
            UPDATE users
            SET password_hash = :hash
            WHERE id = :id
        """), {
            "hash": new_hash,
            "id": user_id
        })

        db.session.commit()

        return jsonify({
            "message": "Password updated successfully"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
