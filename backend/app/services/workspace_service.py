from datetime import datetime, timezone
from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.workspace import Workspace, Milestone, Task, Message, File
from app.models.enums import TaskStatus, MilestoneStatus, UserRole
from app.schemas.workspace import (
    WorkspaceDetailResponse, WorkspaceResponse,
    MilestoneCreate, MilestoneUpdate, MilestoneResponse,
    TaskCreate, TaskUpdate, TaskStatusUpdate, TaskResponse,
    MessageCreate, MessageUpdate, MessageResponse, FileResponse
)
from app.core.errors import NotFoundError, ForbiddenError, BadRequestError
from app.repositories.workspace_repository import WorkspaceRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.team_repository import TeamRepository
from app.services.storage_service import storage_service
from app.services.notification_service import NotificationService


class WorkspaceService:
    def __init__(self, db: Session):
        self.db = db
        self.ws_repo = WorkspaceRepository(db)
        self.project_repo = ProjectRepository(db)
        self.org_repo = OrganizationRepository(db)
        self.student_repo = StudentRepository(db)
        self.team_repo = TeamRepository(db)

    def verify_workspace_access(self, user: User, workspace: Workspace) -> bool:
        if user.role == UserRole.ADMIN:
            return True

        project = self.project_repo.get(workspace.project_id)
        if not project:
            return False

        # If organization owner
        if user.role == UserRole.ORGANIZATION:
            org = self.org_repo.get_by_user_id(user.id)
            if org and project.organization_id == org.id:
                return True

        # If student team member
        if user.role == UserRole.STUDENT:
            student = self.student_repo.get_by_user_id(user.id)
            if student:
                team = self.team_repo.get_by_project_id(project.id)
                if team and any(m.student_id == student.id for m in team.members):
                    return True

        return False

    def get_workspace_by_project(self, user: User, project_id: UUID) -> WorkspaceDetailResponse:
        workspace = self.ws_repo.get_by_project_id(project_id)
        if not workspace:
            raise NotFoundError("Workspace for project", str(project_id))

        if not self.verify_workspace_access(user, workspace):
            raise ForbiddenError("You do not have access to this workspace")

        detailed = self.ws_repo.get_full_workspace(workspace.id)
        return WorkspaceDetailResponse.model_validate(detailed)

    # --- Milestones ---
    def create_milestone(self, user: User, workspace_id: UUID, data_in: MilestoneCreate) -> MilestoneResponse:
        ws = self.ws_repo.get(workspace_id)
        if not ws or not self.verify_workspace_access(user, ws):
            raise ForbiddenError("You do not have access to manage milestones in this workspace")

        milestone = self.ws_repo.create_milestone(workspace_id, data_in.model_dump())
        return MilestoneResponse.model_validate(milestone)

    def update_milestone(self, user: User, milestone_id: UUID, data_in: MilestoneUpdate) -> MilestoneResponse:
        m = self.ws_repo.get_milestone(milestone_id)
        if not m:
            raise NotFoundError("Milestone", str(milestone_id))
        ws = self.ws_repo.get(m.workspace_id)
        if not ws or not self.verify_workspace_access(user, ws):
            raise ForbiddenError("You do not have access to this workspace")

        updated = self.ws_repo.update_milestone(m, data_in.model_dump(exclude_unset=True))
        return MilestoneResponse.model_validate(updated)

    def delete_milestone(self, user: User, milestone_id: UUID) -> None:
        m = self.ws_repo.get_milestone(milestone_id)
        if not m:
            raise NotFoundError("Milestone", str(milestone_id))
        ws = self.ws_repo.get(m.workspace_id)
        if not ws or not self.verify_workspace_access(user, ws):
            raise ForbiddenError("You do not have access to this workspace")
        self.ws_repo.delete_milestone(milestone_id)

    # --- Tasks ---
    def create_task(self, user: User, workspace_id: UUID, data_in: TaskCreate) -> TaskResponse:
        ws = self.ws_repo.get(workspace_id)
        if not ws or not self.verify_workspace_access(user, ws):
            raise ForbiddenError("You do not have access to create tasks in this workspace")

        task = self.ws_repo.create_task(workspace_id, data_in.model_dump())

        # Notify assigned student if task is assigned
        if task.assigned_to:
            student = self.student_repo.get(task.assigned_to)
            if student and student.user_id:
                NotificationService.send_notification(
                    db=self.db,
                    user_id=student.user_id,
                    notif_type="TASK_ASSIGNED",
                    title="New Task Assigned",
                    message=f"You have been assigned to task: '{task.title}'",
                    entity_type="task",
                    entity_id=task.id
                )

        refreshed = self.ws_repo.get_task(task.id)
        return TaskResponse.model_validate(refreshed)

    def update_task(self, user: User, task_id: UUID, data_in: TaskUpdate) -> TaskResponse:
        t = self.ws_repo.get_task(task_id)
        if not t:
            raise NotFoundError("Task", str(task_id))
        ws = self.ws_repo.get(t.workspace_id)
        if not ws or not self.verify_workspace_access(user, ws):
            raise ForbiddenError("You do not have access to this workspace")

        updated = self.ws_repo.update_task(t, data_in.model_dump(exclude_unset=True))
        refreshed = self.ws_repo.get_task(updated.id)
        return TaskResponse.model_validate(refreshed)

    def update_task_status(self, user: User, task_id: UUID, status_in: TaskStatusUpdate) -> TaskResponse:
        t = self.ws_repo.get_task(task_id)
        if not t:
            raise NotFoundError("Task", str(task_id))
        ws = self.ws_repo.get(t.workspace_id)
        if not ws or not self.verify_workspace_access(user, ws):
            raise ForbiddenError("You do not have access to this workspace")

        updated = self.ws_repo.update_task(t, {"status": status_in.status})
        refreshed = self.ws_repo.get_task(updated.id)
        return TaskResponse.model_validate(refreshed)

    def delete_task(self, user: User, task_id: UUID) -> None:
        t = self.ws_repo.get_task(task_id)
        if not t:
            raise NotFoundError("Task", str(task_id))
        ws = self.ws_repo.get(t.workspace_id)
        if not ws or not self.verify_workspace_access(user, ws):
            raise ForbiddenError("You do not have access to this workspace")
        self.ws_repo.delete_task(task_id)

    # --- Messages ---
    def get_messages(self, user: User, workspace_id: UUID, offset: int = 0, limit: int = 50) -> List[MessageResponse]:
        ws = self.ws_repo.get(workspace_id)
        if not ws or not self.verify_workspace_access(user, ws):
            raise ForbiddenError("You do not have access to this workspace")
        msgs = self.ws_repo.get_messages(workspace_id, offset=offset, limit=limit)
        return [MessageResponse.model_validate(m) for m in msgs]

    def send_message(self, user: User, workspace_id: UUID, data_in: MessageCreate) -> MessageResponse:
        ws = self.ws_repo.get(workspace_id)
        if not ws or not self.verify_workspace_access(user, ws):
            raise ForbiddenError("You do not have access to this workspace")
        msg = self.ws_repo.create_message(workspace_id, user.id, data_in.body)
        return MessageResponse.model_validate(msg)

    # --- Files ---
    def upload_file(
        self,
        user: User,
        workspace_id: UUID,
        file_bytes: bytes,
        original_filename: str,
        mime_type: Optional[str] = None
    ) -> FileResponse:
        ws = self.ws_repo.get(workspace_id)
        if not ws or not self.verify_workspace_access(user, ws):
            raise ForbiddenError("You do not have access to upload files to this workspace")

        storage_key, size_bytes = storage_service.upload_file(file_bytes, original_filename, mime_type)
        file_record = self.ws_repo.create_file_record({
            "workspace_id": workspace_id,
            "uploaded_by": user.id,
            "file_name": original_filename,
            "storage_key": storage_key,
            "mime_type": mime_type,
            "file_size_bytes": size_bytes,
            "created_at": datetime.now(timezone.utc)
        })
        return FileResponse.model_validate(file_record)

    def download_file(self, user: User, file_id: UUID) -> Tuple[bytes, str, Optional[str]]:
        file_record = self.ws_repo.get_file(file_id)
        if not file_record:
            raise NotFoundError("File", str(file_id))

        ws = self.ws_repo.get(file_record.workspace_id)
        if not ws or not self.verify_workspace_access(user, ws):
            raise ForbiddenError("You do not have access to this file")

        content = storage_service.get_file_bytes(file_record.storage_key)
        if content is None:
            raise NotFoundError("File content not found in storage")

        return content, file_record.file_name, file_record.mime_type
