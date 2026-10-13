from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from app.models.experience import ExperienceRecord
from app.models.student import StudentProfile
from app.models.feedback import Feedback
from app.models.enums import VerificationStatus
from app.repositories.base import BaseRepository


class ExperienceRepository(BaseRepository[ExperienceRecord]):
    def __init__(self, db: Session):
        super().__init__(ExperienceRecord, db)

    def get_by_slug(self, slug: str) -> Optional[ExperienceRecord]:
        return (
            self.db.query(ExperienceRecord)
            .options(
                joinedload(ExperienceRecord.student),
                joinedload(ExperienceRecord.project),
                joinedload(ExperienceRecord.organization_feedback)
            )
            .filter(ExperienceRecord.public_slug == slug)
            .first()
        )

    def get_by_project_and_student(self, project_id: UUID, student_id: UUID) -> Optional[ExperienceRecord]:
        return (
            self.db.query(ExperienceRecord)
            .filter(
                ExperienceRecord.project_id == project_id,
                ExperienceRecord.student_id == student_id
            )
            .first()
        )

    def list_for_student(
        self,
        student_id: UUID,
        status: Optional[VerificationStatus] = None,
        offset: int = 0,
        limit: int = 20
    ) -> List[ExperienceRecord]:
        query = (
            self.db.query(ExperienceRecord)
            .options(
                joinedload(ExperienceRecord.project),
                joinedload(ExperienceRecord.organization_feedback)
            )
            .filter(ExperienceRecord.student_id == student_id)
        )
        if status:
            query = query.filter(ExperienceRecord.verification_status == status)
        return query.order_by(ExperienceRecord.verified_at.desc().nullslast()).offset(offset).limit(limit).all()

    def count_for_student(self, student_id: UUID, status: Optional[VerificationStatus] = None) -> int:
        query = self.db.query(ExperienceRecord).filter(ExperienceRecord.student_id == student_id)
        if status:
            query = query.filter(ExperienceRecord.verification_status == status)
        return query.count()

    def update_verification_status(
        self,
        record_id: UUID,
        status: VerificationStatus
    ) -> Optional[ExperienceRecord]:
        rec = self.get(record_id)
        if rec:
            rec.verification_status = status
            if status == VerificationStatus.VERIFIED:
                rec.verified_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(rec)
        return rec
