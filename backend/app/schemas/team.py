from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.student import StudentProfilePublicResponse


class TeamMemberCreate(BaseModel):
    student_id: UUID
    role_title: Optional[str] = Field(None, max_length=120)


class TeamMemberResponse(BaseModel):
    team_id: UUID
    student_id: UUID
    role_title: Optional[str] = None
    joined_at: datetime
    student: Optional[StudentProfilePublicResponse] = None

    model_config = ConfigDict(from_attributes=True)


class TeamBase(BaseModel):
    name: str = Field(..., max_length=150)


class TeamCreate(TeamBase):
    project_id: UUID
    members: List[TeamMemberCreate] = []


class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=150)


class TeamResponse(TeamBase):
    id: UUID
    project_id: UUID
    created_by: UUID
    created_at: datetime
    members: List[TeamMemberResponse] = []

    model_config = ConfigDict(from_attributes=True)
