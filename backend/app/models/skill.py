import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.types import GUID


def utcnow():
    return datetime.now(timezone.utc)


class Skill(Base):
    __tablename__ = "skills"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    # Relationships
    student_skills = relationship("StudentSkill", back_populates="skill", cascade="all, delete-orphan")
    project_skills = relationship("ProjectSkill", back_populates="skill", cascade="all, delete-orphan")
