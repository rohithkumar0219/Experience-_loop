from typing import Optional, Dict
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.schemas.common import PaginatedResponse
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/", response_model=PaginatedResponse[NotificationResponse])
def list_my_notifications(
    is_read: Optional[bool] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List notifications for the logged-in user with read/unread filtering."""
    service = NotificationService(db)
    return service.list_my_notifications(current_user, is_read=is_read, page=page, per_page=per_page)


@router.get("/unread-count", response_model=Dict[str, int])
def get_unread_notification_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the count of unread notifications for the logged-in user."""
    service = NotificationService(db)
    count = service.get_unread_count(current_user)
    return {"unread_count": count}


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a specific notification as read."""
    service = NotificationService(db)
    return service.mark_as_read(current_user, notification_id)


@router.post("/read-all", response_model=Dict[str, int])
def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all unread notifications as read for the logged-in user."""
    service = NotificationService(db)
    count = service.mark_all_as_read(current_user)
    return {"marked_read": count}
