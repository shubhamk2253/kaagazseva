from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import text
import models from db
from datetime import datetime, timedelta
import random

auth_bp = Blueprint('auth_bp', __name__)

# --- OTP SYSTEM ---

@auth_bp.route("/api/send-otp", methods=["POST"])
def send_otp():
    data = request.get_json()
    mobile = data.get("mobile")
    login_type = data.get("type")  # 'agent' or 'customer'

    if not mobile:
        return jsonify({"error": "Mobile number is required"}), 400

    # Check if user exists
    user = db.session.execute(text("""
        SELECT id, role FROM users WHERE mobile = :mobile
    """), {"mobile": mobile}).fetchone()

    # 1. Agent Validation: Must exist and be verified
    if login_type == "agent":
        if not user or user.role != "agent":
            return jsonify({"error": "Agent not registered"}), 403

        agent_status = db.session.execute(text("""
            SELECT is_verified FROM agents WHERE id = :id
        """), {"id": user.id}).fetchone()

        if not agent_status or not agent_status.is_verified:
            return jsonify({"error": "Agent account not yet verified"}), 403

    # 2. Customer Auto-Registration: Create user if they don't exist
    if login_type == "customer" and not user:
        db.session.execute(text("""
            INSERT INTO users (id, mobile, role)
            VALUES (gen_random_uuid(), :mobile, 'customer')
        """), {"mobile": mobile})
        db.session.commit()

    # 3. Generate and Store OTP
    otp = str(random.randint(100000, 999999))
    expires = datetime.utcnow() + timedelta(minutes=5)

    db.session.execute(text("""
        INSERT INTO otp_sessions (mobile, otp_code, expires_at)
        VALUES (:mobile, :otp, :expires)
    """), {"mobile": mobile, "otp": otp, "expires": expires})

    db.session.commit()

    # In production, integrate with an SMS gateway here
    print(f"--- DEBUG OTP for {mobile}: {otp} ---")

    return jsonify({"message": "OTP sent successfully"}), 200


@auth_bp.route("/api/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    mobile = data.get("mobile")
    otp = data.get("otp")

    # Fetch valid, unused OTP
    record = db.session.execute(text("""
        SELECT id FROM otp_sessions
        WHERE mobile = :mobile
        AND otp_code = :otp
        AND is_used = FALSE
        AND expires_at > NOW()
        ORDER BY created_at DESC
        LIMIT 1
    """), {"mobile": mobile, "otp": otp}).fetchone()

    if not record:
        return jsonify({"error": "Invalid or expired OTP"}), 400

    # Mark OTP as used
    db.session.execute(text("""
        UPDATE otp_sessions SET is_used = TRUE WHERE id = :id
    """), {"id": record.id})

    # Fetch user details for Token
    user = db.session.execute(text("""
        SELECT id, role FROM users WHERE mobile = :mobile
    """), {"mobile": mobile}).fetchone()

    if not user:
        return jsonify({"error": "User record lost. Please try again."}), 404

    # Generate JWT
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


# --- ADMIN/LEGACY PASSWORD LOGIN ---

def authenticate_user(username, password, expected_role):
    # Standardized to use SQLAlchemy text() for consistency
    user = db.session.execute(text("""
        SELECT id, password_hash, role FROM users WHERE email = :username
    """), {"username": username}).fetchone()

    if user and check_password_hash(user.password_hash, password):
        if user.role == expected_role:
            return create_access_token(
                identity=str(user.id), 
                additional_claims={"role": user.role}
            )
    return None


@auth_bp.route('/api/auth/admin-login', methods=['POST'])
def admin_login():
    data = request.get_json()
    # Admins usually use email/username + password
    token = authenticate_user(data.get('username'), data.get('password'), 'founder')
    if not token:
        return jsonify(msg="Invalid Admin Credentials"), 401
    return jsonify(access_token=token)


@auth_bp.route('/api/auth/change-password', methods=['POST'])
@jwt_required()
def change_password():
    data = request.get_json()
    user_id = get_jwt_identity()
    new_hash = generate_password_hash(data['new_password'])

    db.session.execute(text("""
        UPDATE users SET password_hash = :hash WHERE id = :id
    """), {"hash": new_hash, "id": user_id})
    db.session.commit()

    return jsonify(success=True, message="Password updated successfully"), 200


