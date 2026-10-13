from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.application import Application
from app.models.project import Project
from app.models.team import Team, TeamMember
from app.models.workspace import Workspace
from app.models.enums import ApplicationStatus, ProjectStatus, UserRole
from app.schemas.application import (
    ApplicationCreate, ApplicationUpdate, ApplicationStatusUpdate, ApplicationResponse
)
from app.schemas.common import PaginatedResponse
from app.core.errors import NotFoundError, ForbiddenError, BadRequestError, ConflictError
from app.repositories.application_repository import ApplicationRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.team_repository import TeamRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.repositories.admin_repository import AdminRepository
from app.services.notification_service import NotificationService


class ApplicationService:
    def __init__(self, db: Session):
        self.db = db
        self.app_repo = ApplicationRepository(db)
        self.project_repo = ProjectRepository(db)
        self.student_repo = StudentRepository(db)
        self.org_repo = OrganizationRepository(db)
        self.team_repo = TeamRepository(db)
        self.workspace_repo = WorkspaceRepository(db)
        self.admin_repo = AdminRepository(db)

    def apply_to_project(self, user: User, app_in: ApplicationCreate) -> ApplicationResponse:
        student = self.student_repo.get_by_user_id(user.id)
        if not student:
            raise ForbiddenError("Only students can apply to projects")

        project = self.project_repo.get(app_in.project_id)
        if not project:
            raise NotFoundError("Project", str(app_in.project_id))

        if project.status not in [ProjectStatus.PUBLISHED, ProjectStatus.APPLICATIONS_OPEN]:
            raise BadRequestError(f"Applications are not open for this project (current status: {project.status})")

        # Check existing application
        existing = self.app_repo.get_by_project_and_student(project.id, student.id)
        if existing:
            raise ConflictError("You have already applied to this project")

        app_data = {
            "project_id": project.id,
            "student_id": student.id,
            "cover_message": app_in.cover_message,
            "availability_note": app_in.availability_note,
            "status": ApplicationStatus.PENDING,
            "created_at": datetime.now(timezone.utc)
        }
        application = self.app_repo.create(app_data)

        # Notify organization
        if project.organization and project.organization.user_id:
            NotificationService.send_notification(
                db=self.db,
                user_id=project.organization.user_id,
                notif_type="APPLICATION_RECEIVED",
                title=f"New Application for {project.title}",
                message=f"Student {student.full_name} submitted an application.",
                entity_type="application",
                entity_id=application.id
            )

        return ApplicationResponse.model_validate(application)

    def list_my_applications(
        self,
        user: User,
        status: Optional[ApplicationStatus] = None,
        page: int = 1,
        per_page: int = 20
    ) -> PaginatedResponse[ApplicationResponse]:
        student = self.student_repo.get_by_user_id(user.id)
        if not student:
            raise ForbiddenError("Only students have application records")

        offset = (page - 1) * per_page
        items = self.app_repo.list_for_student(student.id, status=status, offset=offset, limit=per_page)
        total = len(self.app_repo.list_for_student(student.id, status=status, offset=0, limit=1000))
        total_pages = (total + per_page - 1) // per_page if total > 0 else 1

        return PaginatedResponse(
            items=[ApplicationResponse.model_validate(a) for a in items],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )

    def list_applications_for_project(
        self,
        user: User,
        project_id: UUID,
        status: Optional[ApplicationStatus] = None,
        page: int = 1,
        per_page: int = 20
    ) -> PaginatedResponse[ApplicationResponse]:
        project = self.project_repo.get(project_id)
        if not project:
            raise NotFoundError("Project", str(project_id))

        if user.role != UserRole.ADMIN:
            org = self.org_repo.get_by_user_id(user.id)
            if not org or project.organization_id != org.id:
                raise ForbiddenError("You do not have permission to view applications for this project")

        offset = (page - 1) * per_page
        items = self.app_repo.list_for_project(project_id, status=status, offset=offset, limit=per_page)
        total = self.app_repo.count_for_project(project_id, status=status)
        total_pages = (total + per_page - 1) // per_page if total > 0 else 1

        return PaginatedResponse(
            items=[ApplicationResponse.model_validate(a) for a in items],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )

    def update_application_status(
        self,
        user: User,
        application_id: UUID,
        status_in: ApplicationStatusUpdate
    ) -> ApplicationResponse:
        application = self.app_repo.get(application_id)
        if not application:
            raise NotFoundError("Application", str(application_id))

        project = self.project_repo.get(application.project_id)
        if not project:
            raise NotFoundError("Project", str(application.project_id))

        if user.role != UserRole.ADMIN:
            org = self.org_repo.get_by_user_id(user.id)
            if not org or project.organization_id != org.id:
                raise ForbiddenError("You do not have permission to review this application")

        student = self.student_repo.get(application.student_id)
        target_status = status_in.status

        # Execute Transaction-Sensitive Acceptance Workflow
        if target_status == ApplicationStatus.ACCEPTED:
            # 1. Update application status
            application.status = ApplicationStatus.ACCEPTED
            application.reviewed_at = datetime.now(timezone.utc)

            # 2. Create or find Team
            team = self.team_repo.get_by_project_id(project.id)
            if not team:
                team = Team(
                    project_id=project.id,
                    name=f"{project.title} Team",
                    created_by=user.id,
                    created_at=datetime.now(timezone.utc)
                )
                self.db.add(team)
                self.db.flush()

            # 3. Add team member
            self.team_repo.add_member(
                team_id=team.id,
                student_id=student.id,
                role_title="Project Contributor"
            )

            # 4. Create Workspace if not exists
            workspace = self.workspace_repo.get_by_project_id(project.id)
            if not workspace:
                workspace = Workspace(
                    project_id=project.id,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                self.db.add(workspace)
                self.db.flush()

            # 5. Handle conflicting applications if preferred team size is reached
            current_team_members_count = len(team.members) if team.members else 1
            if current_team_members_count >= project.preferred_team_size:
                # Reject remaining pending applications
                pending_apps = (
                    self.db.query(Application)
                    .filter(
                        Application.project_id == project.id,
                        Application.id != application.id,
                        Application.status == ApplicationStatus.PENDING
                    )
                    .all()
                )
                for p_app in pending_apps:
                    p_app.status = ApplicationStatus.REJECTED
                    p_app.reviewed_at = datetime.now(timezone.utc)

            # 6. Move project to IN_PROGRESS
            project.status = ProjectStatus.IN_PROGRESS
            project.updated_at = datetime.now(timezone.utc)

            self.db.commit()
            self.db.refresh(application)

            # 7. Notify student
            if student and student.user_id:
                NotificationService.send_notification(
                    db=self.db,
                    user_id=student.user_id,
                    notif_type="APPLICATION_ACCEPTED",
                    title="Application Accepted!",
                    message=f"Congratulations! You were accepted into project '{project.title}'. The workspace is now ready.",
                    entity_type="project",
                    entity_id=project.id
                )

            # 8. Record audit log
            self.admin_repo.create_audit_log(
                action="APPLICATION_ACCEPTED",
                entity_type="application",
                entity_id=application.id,
                actor_user_id=user.id,
                new_values={"project_id": str(project.id), "student_id": str(student.id)}
            )

            return ApplicationResponse.model_validate(application)

        elif target_status in [ApplicationStatus.REJECTED, ApplicationStatus.SHORTLISTED, ApplicationStatus.WITHDRAWN]:
            application.status = target_status
            application.reviewed_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(application)

            if student and student.user_id:
                msg = f"Your application for project '{project.title}' is now {target_status.value}."
                NotificationService.send_notification(
                    db=self.db,
                    user_id=student.user_id,
                    notif_type=f"APPLICATION_{target_status.value}",
                    title=f"Application {target_status.value.title()}",
                    message=msg,
                    entity_type="application",
                    entity_id=application.id
                )

            return ApplicationResponse.model_validate(application)

        else:
            raise BadRequestError(f"Unsupported status transition to {target_status}")
