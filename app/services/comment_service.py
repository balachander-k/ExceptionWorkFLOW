from app.extensions import db
from app.models import ExceptionComment
from app.services.activity_log_service import ActivityLogService


class CommentService:
    @staticmethod
    def list_for_exception(exception_id):
        return ExceptionComment.query.filter_by(exception_id=exception_id).order_by(ExceptionComment.created_at.asc()).all()

    @staticmethod
    def add(exception_id, user, message, comment_type="GENERAL"):
        comment = ExceptionComment(
            exception_id=exception_id,
            user_id=user.id,
            comment_type=comment_type,
            message=message,
        )
        db.session.add(comment)
        ActivityLogService.log(exception_id, user.id, "COMMENT_ADDED", message)
        db.session.commit()
        return comment

    @staticmethod
    def serialize(comment):
        return {
            "id": comment.id,
            "exception_id": comment.exception_id,
            "user_id": comment.user_id,
            "comment_type": comment.comment_type,
            "message": comment.message,
            "created_at": comment.created_at.isoformat(),
        }
