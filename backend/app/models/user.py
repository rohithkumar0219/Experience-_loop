import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Boolean, DateTime, Enum as SAEnum, Index
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.types import GUID, EnumType
from app.models.enums import UserRole


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    role = Column(EnumType(UserRole, name="user_role"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    # Relationships
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    organization = relationship("Organization", back_populates="user", uselist=False, cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="actor", foreign_keys="AuditLog.actor_user_id")
    reports_submitted = relationship("Report", back_populates="reporter", foreign_keys="Report.reported_by")
    reports_resolved = relationship("Report", back_populates="resolver", foreign_keys="Report.resolved_by")
    submissions = relationship("Submission", back_populates="submitter")
    teams_created = relationship("Team", back_populates="creator")
    messages = relationship("Message", back_populates="sender")
    files_uploaded = relationship("File", back_populates="uploader")

    __table_args__ = (
        Index("idx_users_email", "email", unique=True),
    )
