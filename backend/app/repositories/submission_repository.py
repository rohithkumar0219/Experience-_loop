from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.submission import Submission
from app.models.enums import SubmissionStatus
from app.repositories.base import BaseRepository


class SubmissionRepository(BaseRepository[Submission]):
    def __init__(self, db: Session):
        super().__init__(Submission, db)

    def list_by_project(self, project_id: UUID) -> List[Submission]:
        return (
            self.db.query(Submission)
            .filter(Submission.project_id == project_id)
            .order_by(Submission.submitted_at.desc())
            .all()
        )

    def get_latest_by_project(self, project_id: UUID) -> Optional[Submission]:
        return (
            self.db.query(Submission)
            .filter(Submission.project_id == project_id)
            .order_by(Submission.submitted_at.desc())
            .first()
        )

    def update_status(self, submission_id: UUID, status: SubmissionStatus) -> Optional[Submission]:
        sub = self.get(submission_id)
        if sub:
            sub.status = status
            sub.reviewed_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(sub)
        return sub
