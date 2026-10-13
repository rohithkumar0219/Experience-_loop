from datetime import datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class FeedbackBase(BaseModel):
    technical_implementation: Optional[Decimal] = Field(None, ge=0, le=5)
    requirement_fulfillment: Optional[Decimal] = Field(None, ge=0, le=5)
    communication: Optional[Decimal] = Field(None, ge=0, le=5)
    problem_solving: Optional[Decimal] = Field(None, ge=0, le=5)
    overall_rating: Optional[Decimal] = Field(None, ge=0, le=5)
    comments: Optional[str] = None


class FeedbackCreate(FeedbackBase):
    project_id: UUID
    submission_id: Optional[UUID] = None
    student_id: Optional[UUID] = None


class FeedbackUpdate(FeedbackBase):
    pass


class FeedbackResponse(FeedbackBase):
    id: UUID
    project_id: UUID
    submission_id: Optional[UUID] = None
    organization_id: UUID
    student_id: Optional[UUID] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
