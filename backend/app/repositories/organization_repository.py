from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.organization import Organization
from app.models.enums import OrganizationVerificationStatus
from app.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    def __init__(self, db: Session):
        super().__init__(Organization, db)

    def get_by_user_id(self, user_id: UUID) -> Optional[Organization]:
        return self.db.query(Organization).filter(Organization.user_id == user_id).first()

    def get_by_slug(self, slug: str) -> Optional[Organization]:
        return self.db.query(Organization).filter(Organization.slug == slug).first()

    def list_organizations(
        self,
        status: Optional[OrganizationVerificationStatus] = None,
        search: Optional[str] = None,
        offset: int = 0,
        limit: int = 20
    ) -> List[Organization]:
        query = self.db.query(Organization)
        if status:
            query = query.filter(Organization.verification_status == status)
        if search:
            query = query.filter(
                (Organization.name.ilike(f"%{search}%")) | (Organization.industry.ilike(f"%{search}%"))
            )
        return query.order_by(Organization.name.asc()).offset(offset).limit(limit).all()

    def count_organizations(
        self,
        status: Optional[OrganizationVerificationStatus] = None,
        search: Optional[str] = None
    ) -> int:
        query = self.db.query(Organization)
        if status:
            query = query.filter(Organization.verification_status == status)
        if search:
            query = query.filter(
                (Organization.name.ilike(f"%{search}%")) | (Organization.industry.ilike(f"%{search}%"))
            )
        return query.count()

    def update_verification_status(
        self,
        org_id: UUID,
        status: OrganizationVerificationStatus
    ) -> Optional[Organization]:
        org = self.get(org_id)
        if org:
            org.verification_status = status
            if status == OrganizationVerificationStatus.VERIFIED:
                org.verified_at = datetime.now(timezone.utc)
            else:
                org.verified_at = None
            self.db.commit()
            self.db.refresh(org)
        return org
