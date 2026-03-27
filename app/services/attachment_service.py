from app.extensions import db
from app.models import Attachment
from app.services.activity_log_service import ActivityLogService


class AttachmentService:
    @staticmethod
    def list_for_exception(exception_id):
        return Attachment.query.filter_by(exception_id=exception_id).order_by(Attachment.created_at.asc()).all()

    @staticmethod
    def add(exception_id, user, data):
        attachment = Attachment(
            exception_id=exception_id,
            uploaded_by_user_id=user.id,
            file_name=data["file_name"],
            file_url=data["file_url"],
            mime_type=data["mime_type"],
        )
        db.session.add(attachment)
        ActivityLogService.log(exception_id, user.id, "ATTACHMENT_ADDED", attachment.file_name)
        db.session.commit()
        return attachment

    @staticmethod
    def serialize(attachment):
        return {
            "id": attachment.id,
            "exception_id": attachment.exception_id,
            "uploaded_by_user_id": attachment.uploaded_by_user_id,
            "file_name": attachment.file_name,
            "file_url": attachment.file_url,
            "mime_type": attachment.mime_type,
            "created_at": attachment.created_at.isoformat(),
        }
