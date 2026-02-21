from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt
from flask import jsonify

def role_required(required_role):

    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorated(*args, **kwargs):

            claims = get_jwt()
            role = claims.get("role")

            if role != required_role:
                return jsonify({"error": "Unauthorized"}), 403

            return fn(*args, **kwargs)

        return decorated
    return wrapper
