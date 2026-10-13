import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.types import GUID


def utcnow():
    return datetime.now(timezone.utc)


class Team(Base):
    __tablename__ = "teams"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    created_by = Column(GUID(), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    # Relationships
    project = relationship("Project", back_populates="team")
    creator = relationship("User", back_populates="teams_created")
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    experience_records = relationship("ExperienceRecord", back_populates="team")


class TeamMember(Base):
    __tablename__ = "team_members"

    team_id = Column(GUID(), ForeignKey("teams.id", ondelete="CASCADE"), primary_key=True)
    student_id = Column(GUID(), ForeignKey("student_profiles.id", ondelete="CASCADE"), primary_key=True)
    role_title = Column(String(120), nullable=True)
    joined_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    # Relationships
    team = relationship("Team", back_populates="members")
    student = relationship("StudentProfile", back_populates="team_memberships")

    __table_args__ = (
        Index("idx_team_member", "team_id", "student_id", unique=True),
    )
