import uuid
from sqlalchemy import Column, String, Text, SmallInteger, Numeric, ForeignKey, CheckConstraint, Index, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.types import GUID, EnumType
from app.models.enums import ProficiencyLevel


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    full_name = Column(String(150), nullable=False)
    headline = Column(String(200), nullable=True)
    bio = Column(Text, nullable=True)
    phone = Column(String(30), nullable=True)
    profile_photo_url = Column(Text, nullable=True)
    college = Column(String(200), nullable=True)
    degree = Column(String(150), nullable=True)
    graduation_year = Column(SmallInteger, nullable=True)
    github_url = Column(Text, nullable=True)
    portfolio_url = Column(Text, nullable=True)
    linkedin_url = Column(Text, nullable=True)
    profile_completion = Column(SmallInteger, default=0, nullable=False)

    __table_args__ = (
        CheckConstraint("profile_completion >= 0 AND profile_completion <= 100", name="chk_profile_completion_range"),
    )

    # Relationships
    user = relationship("User", back_populates="student_profile")
    skills = relationship("StudentSkill", back_populates="student", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="student", cascade="all, delete-orphan")
    team_memberships = relationship("TeamMember", back_populates="student", cascade="all, delete-orphan")
    assigned_tasks = relationship("Task", back_populates="assignee")
    feedbacks = relationship("Feedback", back_populates="student")
    experience_records = relationship("ExperienceRecord", back_populates="student")


class StudentSkill(Base):
    __tablename__ = "student_skills"

    student_id = Column(GUID(), ForeignKey("student_profiles.id", ondelete="CASCADE"), primary_key=True)
    skill_id = Column(GUID(), ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)
    proficiency = Column(EnumType(ProficiencyLevel, name="proficiency_level"), nullable=False)
    years_experience = Column(Numeric(3, 1), default=0.0, nullable=False)

    # Relationships
    student = relationship("StudentProfile", back_populates="skills")
    skill = relationship("Skill", back_populates="student_skills")

    __table_args__ = (
        Index("idx_student_skill", "student_id", "skill_id", unique=True),
    )
