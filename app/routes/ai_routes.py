from flask import Blueprint, g, jsonify, request

from app.extensions import db
from app.services.activity_log_service import ActivityLogService
from app.services.ai_service import AIService
from app.utils.auth import require_auth


ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")


@ai_bp.post("/improve-justification")
@require_auth()
def improve_justification():
    body = request.get_json() or {}
    text = body.get("justification", "")
    improved = AIService.improve_justification(text)
    exception_id = body.get("exception_id")
    if exception_id:
        ActivityLogService.log(exception_id, g.current_user.id, "AI_JUSTIFICATION_IMPROVED", "AI improved justification")
        db.session.commit()
    return jsonify({"enhanced_justification": improved})


@ai_bp.post("/generate-summary")
@require_auth()
def generate_summary():
    body = request.get_json() or {}
    summary = AIService.generate_summary(body)
    exception_id = body.get("exception_id")
    if exception_id:
        ActivityLogService.log(exception_id, g.current_user.id, "AI_SUMMARY_GENERATED", summary)
        db.session.commit()
    return jsonify({"summary": summary})


@ai_bp.post("/check-missing-fields")
@require_auth()
def check_missing_fields():
    body = request.get_json() or {}
    message = AIService.check_missing_fields(body)
    return jsonify({"message": message})
