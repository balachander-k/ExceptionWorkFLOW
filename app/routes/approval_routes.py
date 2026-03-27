from flask import Blueprint, g, jsonify, request

from app.models import ApprovalStep
from app.services.approval_service import ApprovalService
from app.utils.auth import require_auth


approval_bp = Blueprint("approvals", __name__, url_prefix="/api/approvals")


@approval_bp.get("/pending")
@require_auth(["REGIONAL_MANAGER", "FINANCE", "SUPPLY_CHAIN", "AUDIT"])
def pending_approvals():
    steps = ApprovalService.pending_for_user(g.current_user)
    return jsonify([ApprovalService.serialize(step) for step in steps])


@approval_bp.post("/<int:approval_id>/action")
@require_auth(["REGIONAL_MANAGER", "FINANCE", "SUPPLY_CHAIN", "AUDIT"])
def approval_action(approval_id):
    step = ApprovalStep.query.get_or_404(approval_id)
    body = request.get_json() or {}
    try:
        acted_step, exception = ApprovalService.act(
            step,
            g.current_user,
            body.get("action", ""),
            body.get("comment", ""),
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(
        {
            "approval_step": ApprovalService.serialize(acted_step),
            "exception_status": exception.status,
        }
    )
