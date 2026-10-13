import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.types import GUID, JSONBType, INETType, EnumType
from app.models.enums import ReportStatus


def utcnow():
    return datetime.now(timezone.utc)


class Report(Base):
    __tablename__ = "reports"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    reported_by = Column(GUID(), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    entity_type = Column(String(80), nullable=False)
    entity_id = Column(GUID(), nullable=False, index=True)
    reason = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        EnumType(ReportStatus, name="report_status"),
        default=ReportStatus.OPEN,
        nullable=False,
        index=True
    )
    resolved_by = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    reporter = relationship("User", back_populates="reports_submitted", foreign_keys=[reported_by])
    resolver = relationship("User", back_populates="reports_resolved", foreign_keys=[resolved_by])


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    actor_user_id = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(120), nullable=False, index=True)
    entity_type = Column(String(80), nullable=False, index=True)
    entity_id = Column(GUID(), nullable=True, index=True)
    old_values = Column(JSONBType(), nullable=True)
    new_values = Column(JSONBType(), nullable=True)
    ip_address = Column(INETType(), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, index=True)

    # Relationships
    actor = relationship("User", back_populates="audit_logs", foreign_keys=[actor_user_id])
