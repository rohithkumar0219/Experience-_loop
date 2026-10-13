from datetime import datetime
from typing import Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import VerificationStatus
from app.schemas.feedback import FeedbackResponse
from app.schemas.student import StudentProfilePublicResponse


class ExperienceRecordBase(BaseModel):
    role_title: str = Field(..., max_length=150)
    problem_solved: str
    technologies: Optional[Any] = None
    deliverables: Optional[Any] = None
    duration_days: Optional[int] = Field(None, ge=1)
    outcome: Optional[str] = None


class ExperienceRecordCreate(ExperienceRecordBase):
    project_id: UUID
    student_id: UUID
    team_id: Optional[UUID] = None
    organization_feedback_id: Optional[UUID] = None
    verification_status: VerificationStatus = VerificationStatus.VERIFIED
    public_slug: Optional[str] = None


class ExperienceRecordUpdate(BaseModel):
    verification_status: Optional[VerificationStatus] = None
    outcome: Optional[str] = None


class ExperienceRecordResponse(ExperienceRecordBase):
    id: UUID
    project_id: UUID
    student_id: UUID
    team_id: Optional[UUID] = None
    organization_feedback_id: Optional[UUID] = None
    verification_status: VerificationStatus
    verified_at: Optional[datetime] = None
    public_slug: str
    organization_feedback: Optional[FeedbackResponse] = None

    model_config = ConfigDict(from_attributes=True)


class ExperienceRecordPublicResponse(ExperienceRecordBase):
    id: UUID
    project_id: UUID
    role_title: str
    problem_solved: str
    technologies: Optional[Any] = None
    deliverables: Optional[Any] = None
    duration_days: Optional[int] = None
    outcome: Optional[str] = None
    verification_status: VerificationStatus
    verified_at: Optional[datetime] = None
    public_slug: str
    student: Optional[StudentProfilePublicResponse] = None
    organization_feedback: Optional[FeedbackResponse] = None

    model_config = ConfigDict(from_attributes=True)
