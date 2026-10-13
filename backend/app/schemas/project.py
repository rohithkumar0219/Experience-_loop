from datetime import datetime, date
from typing import Optional, List, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import ProjectStatus, DifficultyLevel, SkillImportance, ProficiencyLevel
from app.schemas.skill import SkillResponse
from app.schemas.organization import OrganizationPublicResponse


class ProjectSkillBase(BaseModel):
    skill_id: UUID
    importance: SkillImportance = SkillImportance.REQUIRED
    minimum_proficiency: Optional[ProficiencyLevel] = None


class ProjectSkillCreate(ProjectSkillBase):
    pass


class ProjectSkillResponse(BaseModel):
    project_id: UUID
    skill_id: UUID
    importance: SkillImportance
    minimum_proficiency: Optional[ProficiencyLevel] = None
    skill: Optional[SkillResponse] = None

    model_config = ConfigDict(from_attributes=True)


class ProjectBase(BaseModel):
    title: str = Field(..., max_length=250)
    problem_description: str
    difficulty: DifficultyLevel
    estimated_duration_days: Optional[int] = Field(None, ge=1)
    preferred_team_size: int = Field(default=1, ge=1, le=10)
    deliverables: Optional[Any] = None
    structured_brief: Optional[Any] = None
    application_deadline: Optional[datetime] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ProjectCreate(ProjectBase):
    slug: Optional[str] = Field(None, max_length=280)
    skills: List[ProjectSkillCreate] = []


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=250)
    problem_description: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    estimated_duration_days: Optional[int] = Field(None, ge=1)
    preferred_team_size: Optional[int] = Field(None, ge=1, le=10)
    deliverables: Optional[Any] = None
    structured_brief: Optional[Any] = None
    application_deadline: Optional[datetime] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    skills: Optional[List[ProjectSkillCreate]] = None


class ProjectStatusUpdate(BaseModel):
    status: ProjectStatus


class ProjectResponse(ProjectBase):
    id: UUID
    organization_id: UUID
    slug: str
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime
    skills: List[ProjectSkillResponse] = []
    organization: Optional[OrganizationPublicResponse] = None

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    id: UUID
    organization_id: UUID
    title: str
    slug: str
    difficulty: DifficultyLevel
    status: ProjectStatus
    estimated_duration_days: Optional[int] = None
    preferred_team_size: int
    application_deadline: Optional[datetime] = None
    created_at: datetime
    organization_name: Optional[str] = None
    skills: List[ProjectSkillResponse] = []

    model_config = ConfigDict(from_attributes=True)
