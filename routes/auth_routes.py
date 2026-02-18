from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from database import get_db
from services.audit_service import log_audit

auth_bp = Blueprint('auth_bp', __name__)

def authenticate_user(username, password, expected_role):
    with get_db() as conn:
        user = conn.execute(
            "SELECT password_hash, role FROM users WHERE username=?",
            (username,)
        ).fetchone()

    if user and check_password_hash(user['password_hash'], password):
        if user['role'] == expected_role:
            log_audit("LOGIN_SUCCESS", username)
            return create_access_token(identity=username, additional_claims={"role": user['role']})
    log_audit("LOGIN_FAILED", username)
    return None


@auth_bp.route('/api/auth/admin-login', methods=['POST'])
def admin_login():
    data = request.get_json()
    token = authenticate_user(data.get('username'), data.get('password'), 'admin')
    if not token:
        return jsonify(msg="Invalid Credentials"), 401
    return jsonify(access_token=token)


@auth_bp.route('/api/auth/agent-login', methods=['POST'])
def agent_login():
    data = request.get_json()
    token = authenticate_user(data.get('username'), data.get('password'), 'agent')
    if not token:
        return jsonify(msg="Invalid Credentials"), 401
    return jsonify(access_token=token)


@auth_bp.route('/api/auth/change-password', methods=['POST'])
@jwt_required()
def change_password():
    data = request.get_json()
    username = get_jwt_identity()
    new_hash = generate_password_hash(data['new_password'])

    with get_db() as conn:
        conn.execute("UPDATE users SET password_hash=? WHERE username=?", (new_hash, username))
        conn.commit()

    log_audit("PASSWORD_CHANGE", username)
    return jsonify(success=True)
