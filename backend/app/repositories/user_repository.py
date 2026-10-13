from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.enums import UserRole
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        normalized = email.strip().lower()
        return self.db.query(User).filter(User.email == normalized).first()

    def update_last_login(self, user_id: UUID) -> None:
        user = self.get(user_id)
        if user:
            user.last_login_at = datetime.now(timezone.utc)
            self.db.commit()

    def list_users(self, role: Optional[UserRole] = None, is_active: Optional[bool] = None, offset: int = 0, limit: int = 100) -> List[User]:
        query = self.db.query(User)
        if role:
            query = query.filter(User.role == role)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        return query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()

    def count_users(self, role: Optional[UserRole] = None) -> int:
        query = self.db.query(User)
        if role:
            query = query.filter(User.role == role)
        return query.count()
