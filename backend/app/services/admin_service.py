from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.enums import UserRole, OrganizationVerificationStatus, ReportStatus
from app.schemas.user import UserResponse, UserAdminUpdate
from app.schemas.organization import OrganizationResponse
from app.schemas.admin import ReportCreate, ReportResponse, ReportUpdate, AuditLogResponse, DashboardStatsResponse
from app.schemas.common import PaginatedResponse
from app.core.errors import NotFoundError, ForbiddenError
from app.repositories.admin_repository import AdminRepository
from app.repositories.user_repository import UserRepository
from app.repositories.organization_repository import OrganizationRepository


class AdminService:
    def __init__(self, db: Session):
        self.db = db
        self.admin_repo = AdminRepository(db)
        self.user_repo = UserRepository(db)
        self.org_repo = OrganizationRepository(db)

    def list_users(
        self,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        per_page: int = 20
    ) -> PaginatedResponse[UserResponse]:
        offset = (page - 1) * per_page
        items = self.user_repo.list_users(role=role, is_active=is_active, offset=offset, limit=per_page)
        total = self.user_repo.count_users(role=role)
        total_pages = (total + per_page - 1) // per_page if total > 0 else 1

        return PaginatedResponse(
            items=[UserResponse.model_validate(u) for u in items],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )

    def update_user_status(self, admin_user: User, user_id: UUID, update_in: UserAdminUpdate) -> UserResponse:
        target_user = self.user_repo.get(user_id)
        if not target_user:
            raise NotFoundError("User", str(user_id))

        old_vals = {"role": target_user.role.value, "is_active": target_user.is_active, "is_verified": target_user.is_verified}
        if update_in.role:
            target_user.role = update_in.role
        if update_in.is_active is not None:
            target_user.is_active = update_in.is_active
        if update_in.is_verified is not None:
            target_user.is_verified = update_in.is_verified

        self.db.commit()
        self.db.refresh(target_user)

        self.admin_repo.create_audit_log(
            action="ADMIN_UPDATE_USER",
            entity_type="user",
            entity_id=user_id,
            actor_user_id=admin_user.id,
            old_values=old_vals,
            new_values={"role": target_user.role.value, "is_active": target_user.is_active, "is_verified": target_user.is_verified}
        )

        return UserResponse.model_validate(target_user)

    def verify_organization(
        self,
        admin_user: User,
        org_id: UUID,
        status: OrganizationVerificationStatus
    ) -> OrganizationResponse:
        org = self.org_repo.get(org_id)
        if not org:
            raise NotFoundError("Organization", str(org_id))

        old_status = org.verification_status
        updated = self.org_repo.update_verification_status(org_id, status)

        self.admin_repo.create_audit_log(
            action="VERIFY_ORGANIZATION",
            entity_type="organization",
            entity_id=org_id,
            actor_user_id=admin_user.id,
            old_values={"status": old_status.value},
            new_values={"status": status.value}
        )

        return OrganizationResponse.model_validate(updated)

    def list_reports(
        self,
        status: Optional[ReportStatus] = None,
        entity_type: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> PaginatedResponse[ReportResponse]:
        offset = (page - 1) * per_page
        items = self.admin_repo.list_reports(status=status, entity_type=entity_type, offset=offset, limit=per_page)
        total = self.admin_repo.count_reports(status=status)
        total_pages = (total + per_page - 1) // per_page if total > 0 else 1

        return PaginatedResponse(
            items=[ReportResponse.model_validate(r) for r in items],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )

    def create_report(self, user: User, report_in: ReportCreate) -> ReportResponse:
        data = report_in.model_dump()
        data["reported_by"] = user.id
        data["status"] = ReportStatus.OPEN
        report = self.admin_repo.create_report(data)
        return ReportResponse.model_validate(report)

    def resolve_report(self, admin_user: User, report_id: UUID, update_in: ReportUpdate) -> ReportResponse:
        report = self.admin_repo.update_report_status(report_id, update_in.status, admin_user.id)
        if not report:
            raise NotFoundError("Report", str(report_id))

        self.admin_repo.create_audit_log(
            action="RESOLVE_REPORT",
            entity_type="report",
            entity_id=report_id,
            actor_user_id=admin_user.id,
            new_values={"status": update_in.status.value}
        )

        return ReportResponse.model_validate(report)

    def list_audit_logs(
        self,
        entity_type: Optional[str] = None,
        actor_user_id: Optional[UUID] = None,
        action: Optional[str] = None,
        page: int = 1,
        per_page: int = 50
    ) -> PaginatedResponse[AuditLogResponse]:
        offset = (page - 1) * per_page
        items = self.admin_repo.list_audit_logs(
            entity_type=entity_type,
            actor_user_id=actor_user_id,
            action=action,
            offset=offset,
            limit=per_page
        )
        total = self.admin_repo.count_audit_logs(entity_type=entity_type)
        total_pages = (total + per_page - 1) // per_page if total > 0 else 1

        return PaginatedResponse(
            items=[AuditLogResponse.model_validate(l) for l in items],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )

    def get_stats(self) -> DashboardStatsResponse:
        stats = self.admin_repo.get_dashboard_stats()
        return DashboardStatsResponse(**stats)
