from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, UploadFile, File, Response, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.workspace import (
    WorkspaceDetailResponse, MilestoneCreate, MilestoneUpdate, MilestoneResponse,
    TaskCreate, TaskUpdate, TaskStatusUpdate, TaskResponse,
    MessageCreate, MessageResponse, FileResponse
)
from app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


# --- Workspace Details ---
@router.get("/project/{project_id}", response_model=WorkspaceDetailResponse)
def get_workspace_for_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the full workspace details (milestones, tasks, messages, files) for a project."""
    service = WorkspaceService(db)
    return service.get_workspace_by_project(current_user, project_id)


# --- Milestones ---
@router.post("/{workspace_id}/milestones", response_model=MilestoneResponse, status_code=status.HTTP_201_CREATED)
def create_milestone(
    workspace_id: UUID,
    data_in: MilestoneCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a milestone to a project workspace."""
    service = WorkspaceService(db)
    return service.create_milestone(current_user, workspace_id, data_in)


@router.patch("/milestones/{milestone_id}", response_model=MilestoneResponse)
def update_milestone(
    milestone_id: UUID,
    data_in: MilestoneUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a workspace milestone."""
    service = WorkspaceService(db)
    return service.update_milestone(current_user, milestone_id, data_in)


@router.delete("/milestones/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_milestone(
    milestone_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a workspace milestone."""
    service = WorkspaceService(db)
    service.delete_milestone(current_user, milestone_id)
    return None


# --- Tasks ---
@router.post("/{workspace_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    workspace_id: UUID,
    data_in: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a task in the workspace and notify assigned student."""
    service = WorkspaceService(db)
    return service.create_task(current_user, workspace_id, data_in)


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: UUID,
    data_in: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update task details (title, description, priority, assignee, etc.)."""
    service = WorkspaceService(db)
    return service.update_task(current_user, task_id, data_in)


@router.patch("/tasks/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: UUID,
    status_in: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the status of a workspace task (TODO, IN_PROGRESS, BLOCKED, COMPLETED)."""
    service = WorkspaceService(db)
    return service.update_task_status(current_user, task_id, status_in)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a task from the workspace."""
    service = WorkspaceService(db)
    service.delete_task(current_user, task_id)
    return None


# --- Messages ---
@router.get("/{workspace_id}/messages", response_model=List[MessageResponse])
def get_messages(
    workspace_id: UUID,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve message history in the workspace channel."""
    service = WorkspaceService(db)
    return service.get_messages(current_user, workspace_id, offset=offset, limit=limit)


@router.post("/{workspace_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(
    workspace_id: UUID,
    data_in: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Post a communication message in the workspace channel."""
    service = WorkspaceService(db)
    return service.send_message(current_user, workspace_id, data_in)


# --- Files ---
@router.post("/{workspace_id}/files", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    workspace_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a file or deliverable document to the workspace."""
    content = await file.read()
    service = WorkspaceService(db)
    return service.upload_file(
        user=current_user,
        workspace_id=workspace_id,
        file_bytes=content,
        original_filename=file.filename or "upload.bin",
        mime_type=file.content_type
    )


@router.get("/files/{file_id}/download")
def download_file(
    file_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download a file stored in the workspace."""
    service = WorkspaceService(db)
    content, filename, mime_type = service.download_file(current_user, file_id)
    return Response(
        content=content,
        media_type=mime_type or "application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
