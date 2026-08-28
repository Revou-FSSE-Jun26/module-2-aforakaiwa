import bcrypt
from functools import wraps

from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def hash_password(plain_password):
    """Hash a plain text password using bcrypt."""
    return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(plain_password, hashed_password):
    """Verify a plain text password against its bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def roles_required(*roles):
    """Decorator that restricts access to users with specific roles."""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role", "Customer")

            if user_role not in roles:
                return jsonify({
                    "error": "Forbidden",
                    "message": f"Access denied. Required role(s): {', '.join(roles)}"
                }), 403

            return fn(*args, **kwargs)
        return decorator
    return wrapper
