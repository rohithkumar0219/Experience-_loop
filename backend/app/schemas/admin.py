from datetime import datetime
from typing import Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import ReportStatus, UserRole
from app.schemas.user import UserResponse


class ReportCreate(BaseModel):
    entity_type: str = Field(..., max_length=80)
    entity_id: UUID
    reason: str = Field(..., max_length=150)
    description: Optional[str] = None


class ReportUpdate(BaseModel):
    status: ReportStatus


class ReportResponse(BaseModel):
    id: UUID
    reported_by: UUID
    entity_type: str
    entity_id: UUID
    reason: str
    description: Optional[str] = None
    status: ReportStatus
    resolved_by: Optional[UUID] = None
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AuditLogResponse(BaseModel):
    id: UUID
    actor_user_id: Optional[UUID] = None
    action: str
    entity_type: str
    entity_id: Optional[UUID] = None
    old_values: Optional[Any] = None
    new_values: Optional[Any] = None
    ip_address: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserAdminUpdate(BaseModel):
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class DashboardStatsResponse(BaseModel):
    total_users: int
    total_students: int
    total_organizations: int
    total_projects: int
    active_projects: int
    completed_projects: int
    total_applications: int
    verified_experiences: int
    open_reports: int
