from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.models.enums import SubmissionStatus


class SubmissionBase(BaseModel):
    repository_url: Optional[str] = None
    deployment_url: Optional[str] = None
    documentation_url: Optional[str] = None
    demo_url: Optional[str] = None
    notes: Optional[str] = None


class SubmissionCreate(SubmissionBase):
    project_id: UUID


class SubmissionUpdate(SubmissionBase):
    pass


class SubmissionReview(BaseModel):
    status: SubmissionStatus
    notes: Optional[str] = None


class SubmissionResponse(SubmissionBase):
    id: UUID
    project_id: UUID
    submitted_by: UUID
    status: SubmissionStatus
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
