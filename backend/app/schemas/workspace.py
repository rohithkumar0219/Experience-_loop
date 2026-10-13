from datetime import datetime, date
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import MilestoneStatus, TaskPriority, TaskStatus
from app.schemas.student import StudentProfilePublicResponse


# --- Milestones ---
class MilestoneBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    sequence_no: int = 1
    due_date: Optional[date] = None
    status: MilestoneStatus = MilestoneStatus.TODO


class MilestoneCreate(MilestoneBase):
    pass


class MilestoneUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    sequence_no: Optional[int] = None
    due_date: Optional[date] = None
    status: Optional[MilestoneStatus] = None


class MilestoneResponse(MilestoneBase):
    id: UUID
    workspace_id: UUID

    model_config = ConfigDict(from_attributes=True)


# --- Tasks ---
class TaskBase(BaseModel):
    title: str = Field(..., max_length=250)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.TODO
    due_date: Optional[date] = None
    milestone_id: Optional[UUID] = None
    assigned_to: Optional[UUID] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=250)
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[date] = None
    milestone_id: Optional[UUID] = None
    assigned_to: Optional[UUID] = None


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskResponse(TaskBase):
    id: UUID
    workspace_id: UUID
    completed_at: Optional[datetime] = None
    assignee: Optional[StudentProfilePublicResponse] = None

    model_config = ConfigDict(from_attributes=True)


# --- Messages ---
class MessageBase(BaseModel):
    body: str


class MessageCreate(MessageBase):
    pass


class MessageUpdate(BaseModel):
    body: str


class MessageResponse(MessageBase):
    id: UUID
    workspace_id: UUID
    sender_user_id: UUID
    created_at: datetime
    edited_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- Files ---
class FileResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    uploaded_by: UUID
    file_name: str
    storage_key: str
    mime_type: Optional[str] = None
    file_size_bytes: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Workspace ---
class WorkspaceResponse(BaseModel):
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkspaceDetailResponse(WorkspaceResponse):
    milestones: List[MilestoneResponse] = []
    tasks: List[TaskResponse] = []
    messages: List[MessageResponse] = []
    files: List[FileResponse] = []

    model_config = ConfigDict(from_attributes=True)
