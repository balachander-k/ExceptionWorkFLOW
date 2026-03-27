from flask import Blueprint, g, jsonify, request

from app.services.comment_service import CommentService
from app.utils.auth import require_auth


comment_bp = Blueprint("comments", __name__, url_prefix="/api/exceptions/<int:exception_id>/comments")


@comment_bp.get("")
@require_auth()
def list_comments(exception_id):
    comments = CommentService.list_for_exception(exception_id)
    return jsonify([CommentService.serialize(item) for item in comments])


@comment_bp.post("")
@require_auth()
def add_comment(exception_id):
    body = request.get_json() or {}
    message = (body.get("message") or "").strip()
    if not message:
        return jsonify({"error": "message is required"}), 400
    comment = CommentService.add(exception_id, g.current_user, message, body.get("comment_type", "GENERAL"))
    return jsonify(CommentService.serialize(comment)), 201
