from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user, require_student
from app.models.user import User
from app.models.enums import ApplicationStatus
from app.schemas.application import (
    ApplicationCreate, ApplicationStatusUpdate, ApplicationResponse
)
from app.schemas.common import PaginatedResponse
from app.services.application_service import ApplicationService

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def apply_to_project(
    app_in: ApplicationCreate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Apply to a project (Student only)."""
    service = ApplicationService(db)
    return service.apply_to_project(current_user, app_in)


@router.get("/my", response_model=PaginatedResponse[ApplicationResponse])
def list_my_applications(
    status: Optional[ApplicationStatus] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """List all project applications submitted by the logged-in student."""
    service = ApplicationService(db)
    return service.list_my_applications(current_user, status=status, page=page, per_page=per_page)


@router.get("/project/{project_id}", response_model=PaginatedResponse[ApplicationResponse])
def list_applications_for_project(
    project_id: UUID,
    status: Optional[ApplicationStatus] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List applications for a project (Project Organization or Admin)."""
    service = ApplicationService(db)
    return service.list_applications_for_project(current_user, project_id, status=status, page=page, per_page=per_page)


@router.patch("/{application_id}/status", response_model=ApplicationResponse)
def update_application_status(
    application_id: UUID,
    status_in: ApplicationStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Review an application (ACCEPT, SHORTLIST, REJECT).
    Accepting automatically creates or updates the team, adds the student, initializes the workspace,
    and sets the project to IN_PROGRESS in a single transaction.
    """
    service = ApplicationService(db)
    return service.update_application_status(current_user, application_id, status_in)
