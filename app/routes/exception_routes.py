from flask import Blueprint, g, jsonify, request

from app.models import ActivityLog, OpportunityInsight
from app.services.exception_service import ExceptionService
from app.utils.auth import require_auth


exception_bp = Blueprint("exceptions", __name__, url_prefix="/api/exceptions")


@exception_bp.get("")
@require_auth()
def list_exceptions():
    items = ExceptionService.list_all()
    return jsonify([ExceptionService.serialize(item) for item in items])


@exception_bp.get("/<int:exception_id>")
@require_auth()
def get_exception(exception_id):
    item = ExceptionService.get_by_id(exception_id)
    return jsonify(ExceptionService.serialize(item))


@exception_bp.post("")
@require_auth(["STORE_MANAGER"])
def create_exception():
    data = request.get_json() or {}
    try:
        item = ExceptionService.create(data, g.current_user)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(ExceptionService.serialize(item)), 201


@exception_bp.put("/<int:exception_id>")
@require_auth()
def update_exception(exception_id):
    item = ExceptionService.get_by_id(exception_id)
    if item.created_by_user_id != g.current_user.id:
        return jsonify({"error": "Only exception owner can update this exception"}), 403
    data = request.get_json() or {}
    try:
        updated = ExceptionService.update(item, data, g.current_user)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(ExceptionService.serialize(updated))


@exception_bp.post("/<int:exception_id>/submit")
@require_auth()
def submit_exception(exception_id):
    item = ExceptionService.get_by_id(exception_id)
    if item.created_by_user_id != g.current_user.id:
        return jsonify({"error": "Only exception owner can submit this exception"}), 403
    try:
        submitted = ExceptionService.submit(item, g.current_user)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(ExceptionService.serialize(submitted))


@exception_bp.get("/<int:exception_id>/timeline")
@require_auth()
def timeline(exception_id):
    logs = ActivityLog.query.filter_by(exception_id=exception_id).order_by(ActivityLog.created_at.asc()).all()
    return jsonify(
        [
            {
                "id": log.id,
                "exception_id": log.exception_id,
                "actor_user_id": log.actor_user_id,
                "action": log.action,
                "details": log.details,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ]
    )


@exception_bp.get("/<int:exception_id>/opportunities")
@require_auth()
def exception_opportunities(exception_id):
    insights = OpportunityInsight.query.filter_by(exception_id=exception_id).order_by(OpportunityInsight.created_at.desc()).all()
    return jsonify(
        [
            {
                "id": insight.id,
                "exception_id": insight.exception_id,
                "insight_type": insight.insight_type,
                "insight_status": insight.insight_status,
                "description": insight.description,
                "created_at": insight.created_at.isoformat(),
            }
            for insight in insights
        ]
    )
