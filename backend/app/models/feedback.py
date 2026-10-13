import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Text, Numeric, DateTime, ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.types import GUID


def utcnow():
    return datetime.now(timezone.utc)


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    submission_id = Column(GUID(), ForeignKey("submissions.id", ondelete="SET NULL"), nullable=True, index=True)
    organization_id = Column(GUID(), ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True)
    student_id = Column(GUID(), ForeignKey("student_profiles.id", ondelete="SET NULL"), nullable=True, index=True)
    technical_implementation = Column(Numeric(2, 1), nullable=True)
    requirement_fulfillment = Column(Numeric(2, 1), nullable=True)
    communication = Column(Numeric(2, 1), nullable=True)
    problem_solving = Column(Numeric(2, 1), nullable=True)
    overall_rating = Column(Numeric(2, 1), nullable=True)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    # Relationships
    project = relationship("Project", back_populates="feedbacks")
    submission = relationship("Submission", back_populates="feedbacks")
    organization = relationship("Organization", back_populates="feedbacks")
    student = relationship("StudentProfile", back_populates="feedbacks")
    experience_records = relationship("ExperienceRecord", back_populates="organization_feedback")

    __table_args__ = (
        CheckConstraint("technical_implementation >= 0 AND technical_implementation <= 5", name="chk_tech_impl_range"),
        CheckConstraint("requirement_fulfillment >= 0 AND requirement_fulfillment <= 5", name="chk_req_fulfill_range"),
        CheckConstraint("communication >= 0 AND communication <= 5", name="chk_comm_range"),
        CheckConstraint("problem_solving >= 0 AND problem_solving <= 5", name="chk_problem_solv_range"),
        CheckConstraint("overall_rating >= 0 AND overall_rating <= 5", name="chk_overall_rating_range"),
        Index("idx_feedback_project", "project_id"),
        Index("idx_feedback_org", "organization_id"),
        Index("idx_feedback_student", "student_id"),
    )
