from datetime import datetime
from typing import Optional, Any
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from app.models.enums import AnalysisType


class AIStructureRequest(BaseModel):
    project_id: UUID
    problem_description: Optional[str] = None


class AIMatchRequest(BaseModel):
    project_id: UUID
    student_id: Optional[UUID] = None


class AIDifficultyRequest(BaseModel):
    project_id: UUID


class AIRequirementRequest(BaseModel):
    project_id: UUID


class AIProgressRequest(BaseModel):
    project_id: UUID


class AIEvaluationRequest(BaseModel):
    project_id: UUID
    submission_id: Optional[UUID] = None


class AIAnalysisResponse(BaseModel):
    id: UUID
    project_id: UUID
    analysis_type: AnalysisType
    input_snapshot: Any
    output: Any
    model_name: Optional[str] = None
    confidence: Optional[Decimal] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
