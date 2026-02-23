from functools import wraps
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from core.responses import error_response

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            # In JWT we store the role under 'role' claim
            if claims.get("role") != required_role:
                return error_response("Unauthorized access for this role", 403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
