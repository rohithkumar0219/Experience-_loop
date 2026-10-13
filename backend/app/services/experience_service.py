from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.experience import ExperienceRecord
from app.models.enums import VerificationStatus, UserRole
from app.schemas.experience import (
    ExperienceRecordResponse, ExperienceRecordPublicResponse, ExperienceRecordUpdate
)
from app.schemas.common import PaginatedResponse
from app.core.errors import NotFoundError, ForbiddenError
from app.repositories.experience_repository import ExperienceRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.admin_repository import AdminRepository


class ExperienceService:
    def __init__(self, db: Session):
        self.db = db
        self.exp_repo = ExperienceRepository(db)
        self.student_repo = StudentRepository(db)
        self.admin_repo = AdminRepository(db)

    def get_by_public_slug(self, public_slug: str) -> ExperienceRecordPublicResponse:
        record = self.exp_repo.get_by_slug(public_slug)
        if not record:
            raise NotFoundError("Experience record with slug", public_slug)
        return ExperienceRecordPublicResponse.model_validate(record)

    def get_by_id(self, record_id: UUID) -> ExperienceRecordResponse:
        record = self.exp_repo.get(record_id)
        if not record:
            raise NotFoundError("Experience record", str(record_id))
        return ExperienceRecordResponse.model_validate(record)

    def list_student_experiences(
        self,
        student_id: UUID,
        status: Optional[VerificationStatus] = None,
        page: int = 1,
        per_page: int = 20
    ) -> PaginatedResponse[ExperienceRecordResponse]:
        offset = (page - 1) * per_page
        items = self.exp_repo.list_for_student(student_id, status=status, offset=offset, limit=per_page)
        total = self.exp_repo.count_for_student(student_id, status=status)
        total_pages = (total + per_page - 1) // per_page if total > 0 else 1

        return PaginatedResponse(
            items=[ExperienceRecordResponse.model_validate(e) for e in items],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )

    def list_my_experiences(
        self,
        user: User,
        status: Optional[VerificationStatus] = None,
        page: int = 1,
        per_page: int = 20
    ) -> PaginatedResponse[ExperienceRecordResponse]:
        student = self.student_repo.get_by_user_id(user.id)
        if not student:
            raise ForbiddenError("Only student users have experience records")
        return self.list_student_experiences(student.id, status=status, page=page, per_page=per_page)

    def update_verification_status(
        self,
        user: User,
        record_id: UUID,
        status_in: ExperienceRecordUpdate
    ) -> ExperienceRecordResponse:
        if user.role != UserRole.ADMIN:
            raise ForbiddenError("Only administrators can update experience verification status directly")

        record = self.exp_repo.get(record_id)
        if not record:
            raise NotFoundError("Experience record", str(record_id))

        if status_in.verification_status:
            self.exp_repo.update_verification_status(record_id, status_in.verification_status)
        if status_in.outcome:
            record.outcome = status_in.outcome
            self.db.commit()

        refreshed = self.exp_repo.get(record_id)

        self.admin_repo.create_audit_log(
            action="EXPERIENCE_STATUS_CHANGED",
            entity_type="experience_record",
            entity_id=record_id,
            actor_user_id=user.id,
            new_values={"status": status_in.verification_status}
        )

        return ExperienceRecordResponse.model_validate(refreshed)
