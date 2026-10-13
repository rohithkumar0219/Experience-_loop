from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.models.enums import ApplicationStatus
from app.schemas.student import StudentProfilePublicResponse


class ApplicationBase(BaseModel):
    cover_message: Optional[str] = None
    availability_note: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    project_id: UUID


class ApplicationUpdate(BaseModel):
    cover_message: Optional[str] = None
    availability_note: Optional[str] = None


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus


class ApplicationResponse(ApplicationBase):
    id: UUID
    project_id: UUID
    student_id: UUID
    status: ApplicationStatus
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    student: Optional[StudentProfilePublicResponse] = None

    model_config = ConfigDict(from_attributes=True)
