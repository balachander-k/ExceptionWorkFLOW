from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, g, jsonify, request

from app.models import User


def generate_token(user):
    exp = datetime.now(tz=timezone.utc) + timedelta(minutes=current_app.config["JWT_EXP_MINUTES"])
    payload = {"sub": str(user.id), "username": user.username, "role": user.role, "exp": exp}
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def decode_token(token):
    return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])


def require_auth(allowed_roles=None):
    allowed_roles = allowed_roles or []

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            header = request.headers.get("Authorization", "")
            if not header.startswith("Bearer "):
                return jsonify({"error": "Missing bearer token"}), 401
            token = header.replace("Bearer ", "", 1)
            try:
                payload = decode_token(token)
            except jwt.PyJWTError:
                return jsonify({"error": "Invalid token"}), 401
            user = User.query.get(int(payload["sub"]))
            if not user:
                return jsonify({"error": "User not found"}), 401
            if allowed_roles and user.role not in allowed_roles:
                return jsonify({"error": "Forbidden"}), 403
            g.current_user = user
            return fn(*args, **kwargs)

        return wrapper

    return decorator
