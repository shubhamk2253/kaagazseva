from models import db
from sqlalchemy import text
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
import uuid


def log_audit(action, target_id=None):
    """
    Logs system/user actions into audit_logs table.
    Never crashes main transaction.
    """

    performer = "SYSTEM"
    role = "SYSTEM"

    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()

        if identity:
            performer = identity
            role = get_jwt().get("role", "UNKNOWN")

    except Exception:
        # If JWT not present, keep SYSTEM
        pass

    try:
        db.session.execute(text("""
            INSERT INTO audit_logs (
                id,
                action,
                performer,
                role,
                target_id,
                created_at
            )
            VALUES (
                :id,
                :action,
                :performer,
                :role,
                :target,
                NOW()
            )
        """), {
            "id": str(uuid.uuid4()),
            "action": action,
            "performer": performer,
            "role": role,
            "target": target_id
        })

        db.session.commit()

    except Exception:
        # Never allow audit failure to break system
        db.session.rollback()
        pass
