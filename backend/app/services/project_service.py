import re
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.project import Project, ProjectSkill
from app.models.enums import ProjectStatus, DifficultyLevel, UserRole
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectStatusUpdate,
    ProjectResponse, ProjectListResponse, ProjectSkillResponse
)
from app.schemas.common import PaginatedResponse
from app.core.errors import NotFoundError, ForbiddenError, BadRequestError
from app.repositories.project_repository import ProjectRepository
from app.repositories.organization_repository import OrganizationRepository


def generate_project_slug(title: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", title.lower().strip())
    slug = re.sub(r"[-\s]+", "-", cleaned)
    return slug or "project"


class ProjectService:
    def __init__(self, db: Session):
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.org_repo = OrganizationRepository(db)

    def create_project(self, user: User, project_in: ProjectCreate) -> ProjectResponse:
        org = self.org_repo.get_by_user_id(user.id)
        if not org:
            raise ForbiddenError("Only registered organizations can create projects")

        base_slug = project_in.slug or generate_project_slug(project_in.title)
        slug = base_slug
        counter = 1
        while self.project_repo.get_by_slug(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1

        project_data = project_in.model_dump(exclude={"skills", "slug"})
        project_data["organization_id"] = org.id
        project_data["slug"] = slug
        project_data["status"] = ProjectStatus.DRAFT

        project = self.project_repo.create(project_data)

        # Set project skills
        if project_in.skills:
            skills_payload = [s.model_dump() for s in project_in.skills]
            self.project_repo.set_skills(project.id, skills_payload)

        detailed = self.project_repo.get_with_details(project.id)
        return ProjectResponse.model_validate(detailed)

    def get_project_by_id(self, project_id: UUID) -> ProjectResponse:
        project = self.project_repo.get_with_details(project_id)
        if not project:
            raise NotFoundError("Project", str(project_id))
        return ProjectResponse.model_validate(project)

    def get_project_by_slug(self, slug: str) -> ProjectResponse:
        project = self.project_repo.get_by_slug(slug)
        if not project:
            raise NotFoundError("Project", slug)
        return ProjectResponse.model_validate(project)

    def update_project(self, user: User, project_id: UUID, project_in: ProjectUpdate) -> ProjectResponse:
        project = self.project_repo.get_with_details(project_id)
        if not project:
            raise NotFoundError("Project", str(project_id))

        if user.role != UserRole.ADMIN:
            org = self.org_repo.get_by_user_id(user.id)
            if not org or project.organization_id != org.id:
                raise ForbiddenError("You do not have permission to update this project")

        update_data = project_in.model_dump(exclude={"skills"}, exclude_unset=True)
        if update_data:
            self.project_repo.update(project, update_data)

        if project_in.skills is not None:
            skills_payload = [s.model_dump() for s in project_in.skills]
            self.project_repo.set_skills(project.id, skills_payload)

        updated = self.project_repo.get_with_details(project_id)
        return ProjectResponse.model_validate(updated)

    def update_status(self, user: User, project_id: UUID, status_in: ProjectStatusUpdate) -> ProjectResponse:
        project = self.project_repo.get_with_details(project_id)
        if not project:
            raise NotFoundError("Project", str(project_id))

        if user.role != UserRole.ADMIN:
            org = self.org_repo.get_by_user_id(user.id)
            if not org or project.organization_id != org.id:
                raise ForbiddenError("You do not have permission to update this project's status")

        updated = self.project_repo.update_status(project_id, status_in.status)
        detailed = self.project_repo.get_with_details(updated.id)
        return ProjectResponse.model_validate(detailed)

    def list_projects(
        self,
        status: Optional[ProjectStatus] = None,
        difficulty: Optional[DifficultyLevel] = None,
        organization_id: Optional[UUID] = None,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> PaginatedResponse[ProjectListResponse]:
        offset = (page - 1) * per_page
        items = self.project_repo.list_projects(
            status=status,
            difficulty=difficulty,
            organization_id=organization_id,
            search=search,
            offset=offset,
            limit=per_page
        )
        total = self.project_repo.count_projects(
            status=status,
            difficulty=difficulty,
            organization_id=organization_id,
            search=search
        )
        total_pages = (total + per_page - 1) // per_page if total > 0 else 1

        formatted_items = []
        for p in items:
            org_name = p.organization.name if p.organization else None
            skills_resp = [ProjectSkillResponse.model_validate(s) for s in p.skills]
            formatted_items.append(
                ProjectListResponse(
                    id=p.id,
                    organization_id=p.organization_id,
                    title=p.title,
                    slug=p.slug,
                    difficulty=p.difficulty,
                    status=p.status,
                    estimated_duration_days=p.estimated_duration_days,
                    preferred_team_size=p.preferred_team_size,
                    application_deadline=p.application_deadline,
                    created_at=p.created_at,
                    organization_name=org_name,
                    skills=skills_resp
                )
            )

        return PaginatedResponse(
            items=formatted_items,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
