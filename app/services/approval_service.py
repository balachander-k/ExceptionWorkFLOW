from datetime import datetime

from app.constants import APPROVAL_ACTIONS
from app.extensions import db
from app.models import ApprovalStep, Exception, ExceptionComment
from app.services.activity_log_service import ActivityLogService


class ApprovalService:
    @staticmethod
    def _is_step_actionable(step):
        previous = ApprovalStep.query.filter(
            ApprovalStep.exception_id == step.exception_id,
            ApprovalStep.step_order < step.step_order,
        ).order_by(ApprovalStep.step_order.desc()).first()
        if not previous:
            return True
        return previous.status == "APPROVED"

    @staticmethod
    def pending_for_user(user):
        steps = ApprovalStep.query.filter_by(role=user.role, status="PENDING").order_by(ApprovalStep.created_at.asc()).all()
        pending = []
        for step in steps:
            exception = Exception.query.get(step.exception_id)
            if exception.status not in ["SUBMITTED", "IN_REVIEW"]:
                continue
            if ApprovalService._is_step_actionable(step):
                pending.append(step)
        return pending

    @staticmethod
    def act(step, user, action, comment):
        if step.role != user.role:
            raise ValueError("User role cannot action this step")
        if step.status != "PENDING":
            raise ValueError("Approval step already completed")
        if not ApprovalService._is_step_actionable(step):
            raise ValueError("Previous step not yet approved")

        action = action.upper()
        if action not in APPROVAL_ACTIONS:
            raise ValueError("Invalid action")
        if action in ["REJECT", "RETURN"] and not (comment or "").strip():
            raise ValueError("comment is required for REJECT and RETURN actions")

        status_map = {"APPROVE": "APPROVED", "REJECT": "REJECTED", "RETURN": "RETURNED"}
        step.status = status_map[action]
        step.acted_by_user_id = user.id
        step.acted_at = datetime.utcnow()
        step.comment = comment

        exception = Exception.query.get(step.exception_id)

        if comment:
            db.session.add(
                ExceptionComment(
                    exception_id=step.exception_id,
                    user_id=user.id,
                    comment_type="APPROVAL_NOTE",
                    message=comment,
                )
            )

        if action == "APPROVE":
            next_step = ApprovalStep.query.filter(
                ApprovalStep.exception_id == step.exception_id,
                ApprovalStep.step_order > step.step_order,
            ).order_by(ApprovalStep.step_order.asc()).first()
            if next_step:
                exception.status = "IN_REVIEW"
            else:
                exception.status = "APPROVED"
        elif action == "REJECT":
            exception.status = "REJECTED"
        else:
            exception.status = "RETURNED"

        ActivityLogService.log(step.exception_id, user.id, status_map[action], comment)
        db.session.commit()
        return step, exception

    @staticmethod
    def serialize(step):
        return {
            "id": step.id,
            "exception_id": step.exception_id,
            "step_order": step.step_order,
            "role": step.role,
            "status": step.status,
            "acted_by_user_id": step.acted_by_user_id,
            "acted_at": step.acted_at.isoformat() if step.acted_at else None,
            "comment": step.comment,
        }
