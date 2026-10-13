import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Integer, BigInteger, Date, DateTime,
    ForeignKey, Index, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.types import GUID, EnumType
from app.models.enums import MilestoneStatus, TaskPriority, TaskStatus


def utcnow():
    return datetime.now(timezone.utc)


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    # Relationships
    project = relationship("Project", back_populates="workspace")
    milestones = relationship("Milestone", back_populates="workspace", cascade="all, delete-orphan", order_by="Milestone.sequence_no")
    tasks = relationship("Task", back_populates="workspace", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="workspace", cascade="all, delete-orphan", order_by="Message.created_at")
    files = relationship("File", back_populates="workspace", cascade="all, delete-orphan")


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    sequence_no = Column(Integer, nullable=False, default=1)
    due_date = Column(Date, nullable=True)
    status = Column(
        EnumType(MilestoneStatus, name="milestone_status"),
        default=MilestoneStatus.TODO,
        nullable=False
    )

    # Relationships
    workspace = relationship("Workspace", back_populates="milestones")
    tasks = relationship("Task", back_populates="milestone")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    milestone_id = Column(GUID(), ForeignKey("milestones.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_to = Column(GUID(), ForeignKey("student_profiles.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(250), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(
        EnumType(TaskPriority, name="task_priority"),
        default=TaskPriority.MEDIUM,
        nullable=False
    )
    status = Column(
        EnumType(TaskStatus, name="task_status"),
        default=TaskStatus.TODO,
        nullable=False
    )
    due_date = Column(Date, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    workspace = relationship("Workspace", back_populates="tasks")
    milestone = relationship("Milestone", back_populates="tasks")
    assignee = relationship("StudentProfile", back_populates="assigned_tasks")

    __table_args__ = (
        Index("idx_tasks_workspace_status", "workspace_id", "status"),
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_user_id = Column(GUID(), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    edited_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    workspace = relationship("Workspace", back_populates="messages")
    sender = relationship("User", back_populates="messages")


class File(Base):
    __tablename__ = "files"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    uploaded_by = Column(GUID(), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    storage_key = Column(Text, nullable=False)
    mime_type = Column(String(120), nullable=True)
    file_size_bytes = Column(BigInteger, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    # Relationships
    workspace = relationship("Workspace", back_populates="files")
    uploader = relationship("User", back_populates="files_uploaded")
