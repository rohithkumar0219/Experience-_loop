from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.submission import Submission
from app.models.project import Project
from app.models.enums import SubmissionStatus, ProjectStatus, UserRole
from app.schemas.submission import SubmissionCreate, SubmissionUpdate, SubmissionResponse
from app.core.errors import NotFoundError, ForbiddenError, BadRequestError
from app.repositories.submission_repository import SubmissionRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.organization_repository import OrganizationRepository
from app.services.notification_service import NotificationService


class SubmissionService:
    def __init__(self, db: Session):
        self.db = db
        self.sub_repo = SubmissionRepository(db)
        self.project_repo = ProjectRepository(db)
        self.org_repo = OrganizationRepository(db)

    def submit_project(self, user: User, sub_in: SubmissionCreate) -> SubmissionResponse:
        project = self.project_repo.get(sub_in.project_id)
        if not project:
            raise NotFoundError("Project", str(sub_in.project_id))

        if project.status not in [ProjectStatus.IN_PROGRESS, ProjectStatus.SUBMITTED, ProjectStatus.UNDER_REVIEW]:
            raise BadRequestError(f"Cannot submit for project in status: {project.status}")

        sub_data = sub_in.model_dump()
        sub_data["submitted_by"] = user.id
        sub_data["status"] = SubmissionStatus.SUBMITTED
        sub_data["submitted_at"] = datetime.now(timezone.utc)

        submission = self.sub_repo.create(sub_data)

        # Update project status to SUBMITTED
        project.status = ProjectStatus.SUBMITTED
        project.updated_at = datetime.now(timezone.utc)
        self.db.commit()

        # Notify organization
        if project.organization and project.organization.user_id:
            NotificationService.send_notification(
                db=self.db,
                user_id=project.organization.user_id,
                notif_type="SUBMISSION_RECEIVED",
                title=f"New Submission for {project.title}",
                message="A team member has submitted project deliverables for review.",
                entity_type="submission",
                entity_id=submission.id
            )

        return SubmissionResponse.model_validate(submission)

    def list_submissions_for_project(self, user: User, project_id: UUID) -> List[SubmissionResponse]:
        project = self.project_repo.get(project_id)
        if not project:
            raise NotFoundError("Project", str(project_id))

        items = self.sub_repo.list_by_project(project_id)
        return [SubmissionResponse.model_validate(s) for s in items]

    def get_submission(self, user: User, submission_id: UUID) -> SubmissionResponse:
        sub = self.sub_repo.get(submission_id)
        if not sub:
            raise NotFoundError("Submission", str(submission_id))
        return SubmissionResponse.model_validate(sub)
