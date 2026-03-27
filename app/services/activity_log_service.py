from app.extensions import db
from app.models import ActivityLog


class ActivityLogService:
    @staticmethod
    def log(exception_id, actor_user_id, action, details=None):
        entry = ActivityLog(
            exception_id=exception_id,
            actor_user_id=actor_user_id,
            action=action,
            details=details,
        )
        db.session.add(entry)
        return entry
