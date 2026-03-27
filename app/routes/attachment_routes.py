from flask import Blueprint, g, jsonify, request

from app.services.attachment_service import AttachmentService
from app.utils.auth import require_auth


attachment_bp = Blueprint("attachments", __name__, url_prefix="/api/exceptions/<int:exception_id>/attachments")


@attachment_bp.get("")
@require_auth()
def list_attachments(exception_id):
    items = AttachmentService.list_for_exception(exception_id)
    return jsonify([AttachmentService.serialize(item) for item in items])


@attachment_bp.post("")
@require_auth()
def add_attachment(exception_id):
    body = request.get_json() or {}
    required = ["file_name", "file_url", "mime_type"]
    missing = [field for field in required if not body.get(field)]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400
    item = AttachmentService.add(exception_id, g.current_user, body)
    return jsonify(AttachmentService.serialize(item)), 201
