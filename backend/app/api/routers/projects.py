from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user, require_organization, require_org_or_admin
from app.models.user import User
from app.models.enums import ProjectStatus, DifficultyLevel
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectStatusUpdate,
    ProjectResponse, ProjectListResponse
)
from app.schemas.common import PaginatedResponse
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db)
):
    """Create a new project problem statement (Organization role required)."""
    service = ProjectService(db)
    return service.create_project(current_user, project_in)


@router.get("/", response_model=PaginatedResponse[ProjectListResponse])
def list_projects(
    status: Optional[ProjectStatus] = None,
    difficulty: Optional[DifficultyLevel] = None,
    organization_id: Optional[UUID] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Browse and filter projects by status, difficulty, organization, or search keywords."""
    service = ProjectService(db)
    return service.list_projects(
        status=status,
        difficulty=difficulty,
        organization_id=organization_id,
        search=search,
        page=page,
        per_page=per_page
    )


@router.get("/slug/{slug}", response_model=ProjectResponse)
def get_project_by_slug(slug: str, db: Session = Depends(get_db)):
    """Retrieve full project details by unique public slug."""
    service = ProjectService(db)
    return service.get_project_by_slug(slug)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project_by_id(project_id: UUID, db: Session = Depends(get_db)):
    """Retrieve full project details by ID."""
    service = ProjectService(db)
    return service.get_project_by_id(project_id)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: UUID,
    project_in: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update project fields and requirements (Organization owner or Admin)."""
    service = ProjectService(db)
    return service.update_project(current_user, project_id, project_in)


@router.patch("/{project_id}/status", response_model=ProjectResponse)
def update_project_status(
    project_id: UUID,
    status_in: ProjectStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Transition project state (e.g., DRAFT -> PUBLISHED -> APPLICATIONS_OPEN)."""
    service = ProjectService(db)
    return service.update_status(current_user, project_id, status_in)
