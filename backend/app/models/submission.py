import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey, Index, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.types import GUID, EnumType
from app.models.enums import SubmissionStatus


def utcnow():
    return datetime.now(timezone.utc)


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    submitted_by = Column(GUID(), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    repository_url = Column(Text, nullable=True)
    deployment_url = Column(Text, nullable=True)
    documentation_url = Column(Text, nullable=True)
    demo_url = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(
        EnumType(SubmissionStatus, name="submission_status"),
        default=SubmissionStatus.SUBMITTED,
        nullable=False,
        index=True
    )
    submitted_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    project = relationship("Project", back_populates="submissions")
    submitter = relationship("User", back_populates="submissions")
    feedbacks = relationship("Feedback", back_populates="submission")

    __table_args__ = (
        Index("idx_submissions_project", "project_id"),
        Index("idx_submissions_status", "status"),
    )
