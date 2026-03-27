from flask import Blueprint, g, jsonify, request

from app.services.auth_service import AuthService
from app.utils.auth import require_auth


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/login")
def login():
    body = request.get_json() or {}
    result = AuthService.login(body.get("username", ""), body.get("password", ""))
    if not result:
        return jsonify({"error": "Invalid credentials"}), 401
    return jsonify(result)


@auth_bp.get("/me")
@require_auth()
def me():
    user = g.current_user
    return jsonify(
        {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "store_id": user.store_id,
        }
    )
