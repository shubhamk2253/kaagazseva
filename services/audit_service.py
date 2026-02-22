from models import db
from sqlalchemy import text
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt

def log_audit(action, target_id=None):
    username = "SYSTEM"
    role = "SYSTEM"

    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity:
            username = identity
            role = get_jwt().get("role", "UNKNOWN")
    except:
        pass

    db.session.execute(text("""
        INSERT INTO audit_logs(action, performer, role, target_id)
        VALUES (:action, :performer, :role, :target)
    """), {
        "action": action,
        "performer": username,
        "role": role,
        "target": target_id
    })

    db.session.commit()
