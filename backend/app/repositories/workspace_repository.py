from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from app.models.workspace import Workspace, Milestone, Task, Message, File
from app.models.enums import TaskStatus
from app.repositories.base import BaseRepository


class WorkspaceRepository(BaseRepository[Workspace]):
    def __init__(self, db: Session):
        super().__init__(Workspace, db)

    def get_by_project_id(self, project_id: UUID) -> Optional[Workspace]:
        return self.db.query(Workspace).filter(Workspace.project_id == project_id).first()

    def get_full_workspace(self, workspace_id: UUID) -> Optional[Workspace]:
        return (
            self.db.query(Workspace)
            .options(
                joinedload(Workspace.milestones),
                joinedload(Workspace.tasks).joinedload(Task.assignee),
                joinedload(Workspace.messages).joinedload(Message.sender),
                joinedload(Workspace.files).joinedload(File.uploader)
            )
            .filter(Workspace.id == workspace_id)
            .first()
        )

    # --- Milestones ---
    def get_milestones(self, workspace_id: UUID) -> List[Milestone]:
        return (
            self.db.query(Milestone)
            .filter(Milestone.workspace_id == workspace_id)
            .order_by(Milestone.sequence_no.asc())
            .all()
        )

    def create_milestone(self, workspace_id: UUID, data: dict) -> Milestone:
        milestone = Milestone(workspace_id=workspace_id, **data)
        self.db.add(milestone)
        self.db.commit()
        self.db.refresh(milestone)
        return milestone

    def get_milestone(self, milestone_id: UUID) -> Optional[Milestone]:
        return self.db.query(Milestone).filter(Milestone.id == milestone_id).first()

    def update_milestone(self, milestone: Milestone, data: dict) -> Milestone:
        for k, v in data.items():
            if hasattr(milestone, k) and v is not None:
                setattr(milestone, k, v)
        self.db.commit()
        self.db.refresh(milestone)
        return milestone

    def delete_milestone(self, milestone_id: UUID) -> bool:
        m = self.get_milestone(milestone_id)
        if m:
            self.db.delete(m)
            self.db.commit()
            return True
        return False

    # --- Tasks ---
    def get_tasks(self, workspace_id: UUID, status: Optional[TaskStatus] = None) -> List[Task]:
        query = (
            self.db.query(Task)
            .options(joinedload(Task.assignee))
            .filter(Task.workspace_id == workspace_id)
        )
        if status:
            query = query.filter(Task.status == status)
        return query.order_by(Task.due_date.asc().nullslast(), Task.title.asc()).all()

    def get_task(self, task_id: UUID) -> Optional[Task]:
        return (
            self.db.query(Task)
            .options(joinedload(Task.assignee))
            .filter(Task.id == task_id)
            .first()
        )

    def create_task(self, workspace_id: UUID, data: dict) -> Task:
        task = Task(workspace_id=workspace_id, **data)
        if task.status == TaskStatus.COMPLETED and not task.completed_at:
            task.completed_at = datetime.now(timezone.utc)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update_task(self, task: Task, data: dict) -> Task:
        for k, v in data.items():
            if hasattr(task, k) and v is not None:
                setattr(task, k, v)
        if task.status == TaskStatus.COMPLETED and not task.completed_at:
            task.completed_at = datetime.now(timezone.utc)
        elif task.status != TaskStatus.COMPLETED:
            task.completed_at = None
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete_task(self, task_id: UUID) -> bool:
        t = self.get_task(task_id)
        if t:
            self.db.delete(t)
            self.db.commit()
            return True
        return False

    # --- Messages ---
    def get_messages(self, workspace_id: UUID, offset: int = 0, limit: int = 50) -> List[Message]:
        return (
            self.db.query(Message)
            .options(joinedload(Message.sender))
            .filter(Message.workspace_id == workspace_id)
            .order_by(Message.created_at.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def create_message(self, workspace_id: UUID, sender_user_id: UUID, body: str) -> Message:
        message = Message(workspace_id=workspace_id, sender_user_id=sender_user_id, body=body)
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def update_message(self, message: Message, body: str) -> Message:
        message.body = body
        message.edited_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_message(self, message_id: UUID) -> Optional[Message]:
        return self.db.query(Message).filter(Message.id == message_id).first()

    def delete_message(self, message_id: UUID) -> bool:
        m = self.get_message(message_id)
        if m:
            self.db.delete(m)
            self.db.commit()
            return True
        return False

    # --- Files ---
    def get_files(self, workspace_id: UUID) -> List[File]:
        return (
            self.db.query(File)
            .options(joinedload(File.uploader))
            .filter(File.workspace_id == workspace_id)
            .order_by(File.created_at.desc())
            .all()
        )

    def create_file_record(self, data: dict) -> File:
        f = File(**data)
        self.db.add(f)
        self.db.commit()
        self.db.refresh(f)
        return f

    def get_file(self, file_id: UUID) -> Optional[File]:
        return self.db.query(File).filter(File.id == file_id).first()

    def delete_file_record(self, file_id: UUID) -> bool:
        f = self.get_file(file_id)
        if f:
            self.db.delete(f)
            self.db.commit()
            return True
        return False
