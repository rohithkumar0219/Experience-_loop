from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.organization import Organization
from app.models.enums import OrganizationVerificationStatus
from app.schemas.organization import (
    OrganizationUpdate, OrganizationResponse, OrganizationPublicResponse
)
from app.schemas.common import PaginatedResponse
from app.core.errors import NotFoundError, ForbiddenError
from app.repositories.organization_repository import OrganizationRepository


class OrganizationService:
    def __init__(self, db: Session):
        self.db = db
        self.org_repo = OrganizationRepository(db)

    def get_my_organization(self, user: User) -> OrganizationResponse:
        org = self.org_repo.get_by_user_id(user.id)
        if not org:
            raise NotFoundError("Organization profile for current user")
        return OrganizationResponse.model_validate(org)

    def update_my_organization(self, user: User, update_in: OrganizationUpdate) -> OrganizationResponse:
        org = self.org_repo.get_by_user_id(user.id)
        if not org:
            raise NotFoundError("Organization profile for current user")
        updated = self.org_repo.update(org, update_in)
        return OrganizationResponse.model_validate(updated)

    def get_by_slug(self, slug: str) -> OrganizationPublicResponse:
        org = self.org_repo.get_by_slug(slug)
        if not org:
            raise NotFoundError("Organization", slug)
        return OrganizationPublicResponse.model_validate(org)

    def get_by_id(self, org_id: UUID) -> OrganizationPublicResponse:
        org = self.org_repo.get(org_id)
        if not org:
            raise NotFoundError("Organization", str(org_id))
        return OrganizationPublicResponse.model_validate(org)

    def list_organizations(
        self,
        status: Optional[OrganizationVerificationStatus] = None,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> PaginatedResponse[OrganizationPublicResponse]:
        offset = (page - 1) * per_page
        items = self.org_repo.list_organizations(status=status, search=search, offset=offset, limit=per_page)
        total = self.org_repo.count_organizations(status=status, search=search)
        total_pages = (total + per_page - 1) // per_page if total > 0 else 1

        return PaginatedResponse(
            items=[OrganizationPublicResponse.model_validate(o) for o in items],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
