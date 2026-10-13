from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user, require_organization
from app.models.user import User
from app.models.enums import OrganizationVerificationStatus
from app.schemas.organization import (
    OrganizationResponse, OrganizationPublicResponse, OrganizationUpdate
)
from app.schemas.common import PaginatedResponse
from app.services.organization_service import OrganizationService

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get("/me", response_model=OrganizationResponse)
def get_my_organization(
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db)
):
    """Retrieve the current logged-in organization's profile and verification status."""
    service = OrganizationService(db)
    return service.get_my_organization(current_user)


@router.put("/me", response_model=OrganizationResponse)
def update_my_organization(
    org_in: OrganizationUpdate,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db)
):
    """Update current organization profile information."""
    service = OrganizationService(db)
    return service.update_my_organization(current_user, org_in)


@router.get("/", response_model=PaginatedResponse[OrganizationPublicResponse])
def list_organizations(
    status: Optional[OrganizationVerificationStatus] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Browse organizations with optional status filtering and name search."""
    service = OrganizationService(db)
    return service.list_organizations(status=status, search=search, page=page, per_page=per_page)


@router.get("/slug/{slug}", response_model=OrganizationPublicResponse)
def get_organization_by_slug(slug: str, db: Session = Depends(get_db)):
    """Retrieve public organization details by slug."""
    service = OrganizationService(db)
    return service.get_by_slug(slug)


@router.get("/{org_id}", response_model=OrganizationPublicResponse)
def get_organization_by_id(org_id: UUID, db: Session = Depends(get_db)):
    """Retrieve public organization details by ID."""
    service = OrganizationService(db)
    return service.get_by_id(org_id)
