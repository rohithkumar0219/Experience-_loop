import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, SmallInteger, Integer, Date, DateTime,
    ForeignKey, Index, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.types import GUID, JSONBType, EnumType
from app.models.enums import ProjectStatus, DifficultyLevel, SkillImportance, ProficiencyLevel


def utcnow():
    return datetime.now(timezone.utc)


class Project(Base):
    __tablename__ = "projects"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    organization_id = Column(GUID(), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(250), nullable=False)
    slug = Column(String(280), unique=True, nullable=False, index=True)
    problem_description = Column(Text, nullable=False)
    structured_brief = Column(JSONBType(), nullable=True)
    deliverables = Column(JSONBType(), nullable=True)
    difficulty = Column(EnumType(DifficultyLevel, name="project_difficulty"), nullable=False)
    estimated_duration_days = Column(Integer, nullable=True)
    preferred_team_size = Column(SmallInteger, default=1, nullable=False)
    status = Column(
        EnumType(ProjectStatus, name="project_status"),
        default=ProjectStatus.DRAFT,
        nullable=False,
        index=True
    )
    application_deadline = Column(DateTime(timezone=True), nullable=True, index=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="projects")
    skills = relationship("ProjectSkill", back_populates="project", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="project", cascade="all, delete-orphan")
    team = relationship("Team", back_populates="project", uselist=False, cascade="all, delete-orphan")
    workspace = relationship("Workspace", back_populates="project", uselist=False, cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="project", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="project", cascade="all, delete-orphan")
    experience_records = relationship("ExperienceRecord", back_populates="project", cascade="all, delete-orphan")
    ai_analyses = relationship("AIAnalysis", back_populates="project", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_projects_status", "status"),
        Index("idx_projects_org", "organization_id"),
        Index("idx_projects_difficulty", "difficulty"),
        Index("idx_projects_deadline", "application_deadline"),
    )


class ProjectSkill(Base):
    __tablename__ = "project_skills"

    project_id = Column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    skill_id = Column(GUID(), ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)
    importance = Column(
        EnumType(SkillImportance, name="skill_importance"),
        default=SkillImportance.REQUIRED,
        nullable=False
    )
    minimum_proficiency = Column(
        EnumType(ProficiencyLevel, name="min_proficiency_level"),
        nullable=True
    )

    # Relationships
    project = relationship("Project", back_populates="skills")
    skill = relationship("Skill", back_populates="project_skills")

    __table_args__ = (
        Index("idx_project_skill", "project_id", "skill_id", unique=True),
    )
