from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user, require_admin, require_student
from app.models.user import User
from app.models.enums import VerificationStatus
from app.schemas.experience import (
    ExperienceRecordResponse, ExperienceRecordPublicResponse, ExperienceRecordUpdate
)
from app.schemas.common import PaginatedResponse
from app.services.experience_service import ExperienceService

router = APIRouter(prefix="/experience", tags=["Experience Records"])


@router.get("/public/{public_slug}", response_model=ExperienceRecordPublicResponse)
def get_public_experience_record(
    public_slug: str,
    db: Session = Depends(get_db)
):
    """Publicly accessible endpoint to verify an experience record via its immutable slug."""
    service = ExperienceService(db)
    return service.get_by_public_slug(public_slug)


@router.get("/my", response_model=PaginatedResponse[ExperienceRecordResponse])
def list_my_experience_records(
    status: Optional[VerificationStatus] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """List verified experience records for the logged-in student."""
    service = ExperienceService(db)
    return service.list_my_experiences(current_user, status=status, page=page, per_page=per_page)


@router.get("/student/{student_id}", response_model=PaginatedResponse[ExperienceRecordResponse])
def list_student_experience_records(
    student_id: UUID,
    status: Optional[VerificationStatus] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List verified experience records for a specific student."""
    service = ExperienceService(db)
    return service.list_student_experiences(student_id, status=status, page=page, per_page=per_page)


@router.get("/{record_id}", response_model=ExperienceRecordResponse)
def get_experience_record(
    record_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get experience record by ID."""
    service = ExperienceService(db)
    return service.get_by_id(record_id)


@router.patch("/{record_id}/status", response_model=ExperienceRecordResponse)
def update_experience_verification_status(
    record_id: UUID,
    status_in: ExperienceRecordUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update experience verification status (Admin only)."""
    service = ExperienceService(db)
    return service.update_verification_status(current_user, record_id, status_in)
