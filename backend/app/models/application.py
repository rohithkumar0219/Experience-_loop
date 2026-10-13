import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey, Index, UniqueConstraint, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.types import GUID, EnumType
from app.models.enums import ApplicationStatus


def utcnow():
    return datetime.now(timezone.utc)


class Application(Base):
    __tablename__ = "applications"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(GUID(), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    cover_message = Column(Text, nullable=True)
    availability_note = Column(Text, nullable=True)
    status = Column(
        EnumType(ApplicationStatus, name="application_status"),
        default=ApplicationStatus.PENDING,
        nullable=False,
        index=True
    )
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    # Relationships
    project = relationship("Project", back_populates="applications")
    student = relationship("StudentProfile", back_populates="applications")

    __table_args__ = (
        UniqueConstraint("project_id", "student_id", name="uq_project_student_application"),
        Index("idx_applications_project", "project_id"),
        Index("idx_applications_student", "student_id"),
        Index("idx_applications_status", "status"),
    )
