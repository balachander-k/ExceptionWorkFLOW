from datetime import datetime
from decimal import Decimal, InvalidOperation

from app.extensions import db
from app.models import ApprovalStep, Exception, ExceptionType, Store
from app.services.activity_log_service import ActivityLogService
from app.services.opportunity_service import OpportunityService


class ExceptionService:
    REQUIRED_FIELDS = ["store_id", "exception_type_id", "title", "description", "justification", "amount"]

    @staticmethod
    def _validate_payload(data, partial=False):
        if not partial:
            missing = [field for field in ExceptionService.REQUIRED_FIELDS if field not in data]
            if missing:
                raise ValueError(f"Missing required fields: {', '.join(missing)}")

        candidate = data.copy()
        if "amount" in candidate:
            try:
                amount = Decimal(str(candidate["amount"]))
            except (InvalidOperation, TypeError):
                raise ValueError("amount must be a valid numeric value") from None
            if amount <= 0:
                raise ValueError("amount must be greater than 0")
            candidate["amount"] = amount

        if "exception_type_id" in candidate:
            ex_type = ExceptionType.query.get(candidate["exception_type_id"])
            if not ex_type:
                raise ValueError("Invalid exception_type_id")

        if "store_id" in candidate:
            store = Store.query.get(candidate["store_id"])
            if not store:
                raise ValueError("Invalid store_id")

        return candidate

    @staticmethod
    def _next_exception_number():
        latest = Exception.query.order_by(Exception.id.desc()).first()
        next_id = 1 if not latest else latest.id + 1
        return f"EXC-{next_id:06d}"

    @staticmethod
    def create(data, user):
        valid_data = ExceptionService._validate_payload(data, partial=False)
        exception = Exception(
            exception_number=ExceptionService._next_exception_number(),
            store_id=valid_data["store_id"],
            exception_type_id=valid_data["exception_type_id"],
            title=valid_data["title"],
            description=valid_data["description"],
            justification=valid_data["justification"],
            amount=valid_data["amount"],
            status="DRAFT",
            created_by_user_id=user.id,
        )
        db.session.add(exception)
        db.session.flush()
        ActivityLogService.log(exception.id, user.id, "EXCEPTION_CREATED", "Exception created in DRAFT state")
        db.session.commit()
        return exception

    @staticmethod
    def update(exception, data, user):
        if exception.status not in ["DRAFT", "RETURNED"]:
            raise ValueError("Only DRAFT or RETURNED exceptions can be updated")
        valid_data = ExceptionService._validate_payload(data, partial=True)
        for field in ["title", "description", "justification", "amount", "store_id", "exception_type_id"]:
            if field in valid_data:
                setattr(exception, field, valid_data[field])
        ActivityLogService.log(exception.id, user.id, "EXCEPTION_UPDATED", "Exception details updated")
        db.session.commit()
        return exception

    @staticmethod
    def build_approval_chain(exception_type):
        chain_text = exception_type.default_approval_chain.strip()
        roles = [role.strip() for role in chain_text.split(",") if role.strip()]
        if not roles:
            roles = ["REGIONAL_MANAGER", "FINANCE", "AUDIT"]
        return roles

    @staticmethod
    def submit(exception, user):
        if exception.status not in ["DRAFT", "RETURNED"]:
            raise ValueError("Only DRAFT or RETURNED exceptions can be submitted")

        ApprovalStep.query.filter_by(exception_id=exception.id).delete()
        roles = ExceptionService.build_approval_chain(exception.exception_type)
        for idx, role in enumerate(roles, start=1):
            step = ApprovalStep(
                exception_id=exception.id,
                step_order=idx,
                role=role,
                status="PENDING",
            )
            db.session.add(step)

        exception.status = "SUBMITTED"
        exception.submitted_at = datetime.utcnow()
        ActivityLogService.log(exception.id, user.id, "SUBMITTED", "Exception submitted for approvals")

        insights = OpportunityService.evaluate(exception)
        for insight in insights:
            ActivityLogService.log(exception.id, user.id, "INSIGHT_GENERATED", insight.insight_type)

        db.session.commit()
        return exception

    @staticmethod
    def list_all():
        return Exception.query.order_by(Exception.created_at.desc()).all()

    @staticmethod
    def get_by_id(exception_id):
        return Exception.query.get_or_404(exception_id)

    @staticmethod
    def serialize(exception):
        return {
            "id": exception.id,
            "exception_number": exception.exception_number,
            "store_id": exception.store_id,
            "exception_type_id": exception.exception_type_id,
            "exception_type": exception.exception_type.code,
            "title": exception.title,
            "description": exception.description,
            "justification": exception.justification,
            "amount": float(exception.amount),
            "status": exception.status,
            "created_by_user_id": exception.created_by_user_id,
            "submitted_at": exception.submitted_at.isoformat() if exception.submitted_at else None,
            "created_at": exception.created_at.isoformat(),
            "updated_at": exception.updated_at.isoformat(),
        }
