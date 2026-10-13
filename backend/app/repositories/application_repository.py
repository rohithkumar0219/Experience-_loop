from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from app.models.application import Application
from app.models.student import StudentProfile
from app.models.enums import ApplicationStatus
from app.repositories.base import BaseRepository


class ApplicationRepository(BaseRepository[Application]):
    def __init__(self, db: Session):
        super().__init__(Application, db)

    def get_by_project_and_student(self, project_id: UUID, student_id: UUID) -> Optional[Application]:
        return (
            self.db.query(Application)
            .filter(Application.project_id == project_id, Application.student_id == student_id)
            .first()
        )

    def list_for_project(
        self,
        project_id: UUID,
        status: Optional[ApplicationStatus] = None,
        offset: int = 0,
        limit: int = 50
    ) -> List[Application]:
        query = (
            self.db.query(Application)
            .options(joinedload(Application.student))
            .filter(Application.project_id == project_id)
        )
        if status:
            query = query.filter(Application.status == status)
        return query.order_by(Application.created_at.asc()).offset(offset).limit(limit).all()

    def count_for_project(self, project_id: UUID, status: Optional[ApplicationStatus] = None) -> int:
        query = self.db.query(Application).filter(Application.project_id == project_id)
        if status:
            query = query.filter(Application.status == status)
        return query.count()

    def list_for_student(
        self,
        student_id: UUID,
        status: Optional[ApplicationStatus] = None,
        offset: int = 0,
        limit: int = 50
    ) -> List[Application]:
        query = (
            self.db.query(Application)
            .options(joinedload(Application.project))
            .filter(Application.student_id == student_id)
        )
        if status:
            query = query.filter(Application.status == status)
        return query.order_by(Application.created_at.desc()).offset(offset).limit(limit).all()

    def update_status(self, application_id: UUID, status: ApplicationStatus) -> Optional[Application]:
        app = self.get(application_id)
        if app:
            app.status = status
            app.reviewed_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(app)
        return app
