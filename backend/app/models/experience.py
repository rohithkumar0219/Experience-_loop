import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Index, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.types import GUID, JSONBType, EnumType
from app.models.enums import VerificationStatus


def utcnow():
    return datetime.now(timezone.utc)


class ExperienceRecord(Base):
    __tablename__ = "experience_records"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID(), ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False, index=True)
    student_id = Column(GUID(), ForeignKey("student_profiles.id", ondelete="RESTRICT"), nullable=False, index=True)
    team_id = Column(GUID(), ForeignKey("teams.id", ondelete="SET NULL"), nullable=True, index=True)
    role_title = Column(String(150), nullable=False)
    problem_solved = Column(Text, nullable=False)
    technologies = Column(JSONBType(), nullable=True)
    deliverables = Column(JSONBType(), nullable=True)
    duration_days = Column(Integer, nullable=True)
    outcome = Column(Text, nullable=True)
    organization_feedback_id = Column(GUID(), ForeignKey("feedback.id", ondelete="SET NULL"), nullable=True, index=True)
    verification_status = Column(
        EnumType(VerificationStatus, name="experience_verification_status"),
        default=VerificationStatus.PENDING,
        nullable=False,
        index=True
    )
    verified_at = Column(DateTime(timezone=True), nullable=True)
    public_slug = Column(String(250), unique=True, nullable=False, index=True)

    # Relationships
    project = relationship("Project", back_populates="experience_records")
    student = relationship("StudentProfile", back_populates="experience_records")
    team = relationship("Team", back_populates="experience_records")
    organization_feedback = relationship("Feedback", back_populates="experience_records")

    __table_args__ = (
        Index("idx_experience_student", "student_id"),
        Index("idx_experience_project", "project_id"),
        Index("idx_experience_slug", "public_slug", unique=True),
    )
