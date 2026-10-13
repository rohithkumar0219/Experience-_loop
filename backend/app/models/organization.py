import uuid
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.types import GUID, EnumType
from app.models.enums import OrganizationVerificationStatus


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(220), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    website_url = Column(Text, nullable=True)
    logo_url = Column(Text, nullable=True)
    industry = Column(String(120), nullable=True)
    location = Column(String(200), nullable=True)
    verification_status = Column(
        EnumType(OrganizationVerificationStatus, name="organization_verification_status"),
        default=OrganizationVerificationStatus.PENDING,
        nullable=False
    )
    verified_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="organization")
    projects = relationship("Project", back_populates="organization", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="organization")
