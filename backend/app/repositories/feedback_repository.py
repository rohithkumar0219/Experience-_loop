from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.feedback import Feedback
from app.repositories.base import BaseRepository


class FeedbackRepository(BaseRepository[Feedback]):
    def __init__(self, db: Session):
        super().__init__(Feedback, db)

    def list_by_project(self, project_id: UUID) -> List[Feedback]:
        return (
            self.db.query(Feedback)
            .filter(Feedback.project_id == project_id)
            .order_by(Feedback.created_at.desc())
            .all()
        )

    def get_by_submission(self, submission_id: UUID) -> Optional[Feedback]:
        return self.db.query(Feedback).filter(Feedback.submission_id == submission_id).first()

    def list_by_student(self, student_id: UUID) -> List[Feedback]:
        return (
            self.db.query(Feedback)
            .filter(Feedback.student_id == student_id)
            .order_by(Feedback.created_at.desc())
            .all()
        )
