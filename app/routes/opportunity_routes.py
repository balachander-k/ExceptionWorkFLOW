from flask import Blueprint, jsonify

from app.models import OpportunityInsight
from app.utils.auth import require_auth


opportunity_bp = Blueprint("opportunities", __name__, url_prefix="/api/opportunities")


@opportunity_bp.get("")
@require_auth()
def list_all_opportunities():
    insights = OpportunityInsight.query.order_by(OpportunityInsight.created_at.desc()).all()
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
