from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.user import User
from app.models.enums import UserRole, OrganizationVerificationStatus, ReportStatus
from app.schemas.user import UserResponse, UserAdminUpdate
from app.schemas.organization import OrganizationResponse
from app.schemas.admin import (
    ReportCreate, ReportUpdate, ReportResponse, AuditLogResponse, DashboardStatsResponse
)
from app.schemas.common import PaginatedResponse
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get system-wide platform statistics for administrators."""
    service = AdminService(db)
    return service.get_stats()


# --- User Management ---
@router.get("/users", response_model=PaginatedResponse[UserResponse])
def list_users(
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List and filter users across the platform."""
    service = AdminService(db)
    return service.list_users(role=role, is_active=is_active, page=page, per_page=per_page)


@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user_status(
    user_id: UUID,
    update_in: UserAdminUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update user role, active status, or verification status."""
    service = AdminService(db)
    return service.update_user_status(current_user, user_id, update_in)


# --- Organization Verification ---
@router.patch("/organizations/{organization_id}/verify", response_model=OrganizationResponse)
def verify_organization(
    organization_id: UUID,
    status: OrganizationVerificationStatus,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Verify or reject an organization profile."""
    service = AdminService(db)
    return service.verify_organization(current_user, organization_id, status)


# --- Reports ---
@router.post("/reports", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def submit_report(
    report_in: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """File a report against an entity (project, user, workspace, etc.)."""
    service = AdminService(db)
    return service.create_report(current_user, report_in)


@router.get("/reports", response_model=PaginatedResponse[ReportResponse])
def list_reports(
    status: Optional[ReportStatus] = None,
    entity_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List flagged reports for admin review."""
    service = AdminService(db)
    return service.list_reports(status=status, entity_type=entity_type, page=page, per_page=per_page)


@router.patch("/reports/{report_id}/resolve", response_model=ReportResponse)
def resolve_report(
    report_id: UUID,
    update_in: ReportUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Resolve, dismiss, or update the status of a report."""
    service = AdminService(db)
    return service.resolve_report(current_user, report_id, update_in)


# --- Audit Logs ---
@router.get("/audit-logs", response_model=PaginatedResponse[AuditLogResponse])
def list_audit_logs(
    entity_type: Optional[str] = None,
    actor_user_id: Optional[UUID] = None,
    action: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """View immutable system audit logs for administrative oversight."""
    service = AdminService(db)
    return service.list_audit_logs(
        entity_type=entity_type,
        actor_user_id=actor_user_id,
        action=action,
        page=page,
        per_page=per_page
    )
