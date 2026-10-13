from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.schemas.common import PaginatedResponse
from app.core.errors import NotFoundError, ForbiddenError
from app.repositories.notification_repository import NotificationRepository


class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.notif_repo = NotificationRepository(db)

    @staticmethod
    def send_notification(
        db: Session,
        user_id: UUID,
        notif_type: str,
        title: str,
        message: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None
    ) -> Notification:
        """Helper to create and persist in-app notifications for users."""
        notification = Notification(
            user_id=user_id,
            type=notif_type,
            title=title,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
            is_read=False
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    def list_my_notifications(
        self,
        user: User,
        is_read: Optional[bool] = None,
        page: int = 1,
        per_page: int = 20
    ) -> PaginatedResponse[NotificationResponse]:
        offset = (page - 1) * per_page
        items = self.notif_repo.list_for_user(user.id, is_read=is_read, offset=offset, limit=per_page)
        
        # Count
        query = self.db.query(Notification).filter(Notification.user_id == user.id)
        if is_read is not None:
            query = query.filter(Notification.is_read == is_read)
        total = query.count()
        total_pages = (total + per_page - 1) // per_page if total > 0 else 1

        return PaginatedResponse(
            items=[NotificationResponse.model_validate(n) for n in items],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )

    def mark_as_read(self, user: User, notification_id: UUID) -> NotificationResponse:
        notif = self.notif_repo.get(notification_id)
        if not notif:
            raise NotFoundError("Notification", str(notification_id))
        if notif.user_id != user.id:
            raise ForbiddenError("Cannot modify another user's notification")
        
        notif.is_read = True
        self.db.commit()
        self.db.refresh(notif)
        return NotificationResponse.model_validate(notif)

    def mark_all_as_read(self, user: User) -> int:
        return self.notif_repo.mark_all_read(user.id)

    def get_unread_count(self, user: User) -> int:
        return self.notif_repo.count_unread(user.id)

