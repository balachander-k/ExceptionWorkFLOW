from decimal import Decimal

from app.extensions import db
from app.models import OpportunityInsight


class OpportunityService:
    @staticmethod
    def evaluate(exception):
        rules = []
        ex_type_code = exception.exception_type.code
        amount = Decimal(exception.amount)
        justification_lower = (exception.justification or "").lower()

        if ex_type_code == "PRICING_OVERRIDE" and amount > Decimal("1000"):
            rules.append(("REVENUE_RECOVERY", "High-value pricing override may indicate recoverable margin."))

        if ex_type_code == "CUSTOMER_COMPENSATION" and "offer" in justification_lower:
            rules.append(("UNCLAIMED_OFFER", "Customer compensation references an offer that can be tracked for optimization."))

        if ex_type_code == "INVENTORY_WRITEOFF" and amount > Decimal("5000"):
            rules.append(("LOSS_ALERT", "Large inventory write-off detected; potential loss prevention initiative."))

        if ex_type_code == "SUPPLIER_SHORT_DELIVERY" and amount > Decimal("10000"):
            rules.append(("REVENUE_RECOVERY", "Major supplier short delivery could support vendor recovery claims."))

        created = []
        for insight_type, description in rules:
            existing = OpportunityInsight.query.filter_by(
                exception_id=exception.id,
                insight_type=insight_type,
            ).first()
            if existing:
                continue
            insight = OpportunityInsight(
                exception_id=exception.id,
                insight_type=insight_type,
                insight_status="OPEN",
                description=description,
            )
            db.session.add(insight)
            created.append(insight)

        return created
