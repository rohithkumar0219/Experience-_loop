from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.team import Team, TeamMember
from app.models.enums import UserRole
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse, TeamMemberCreate, TeamMemberResponse
from app.core.errors import NotFoundError, ForbiddenError, BadRequestError
from app.repositories.team_repository import TeamRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.student_repository import StudentRepository


class TeamService:
    def __init__(self, db: Session):
        self.db = db
        self.team_repo = TeamRepository(db)
        self.project_repo = ProjectRepository(db)
        self.org_repo = OrganizationRepository(db)
        self.student_repo = StudentRepository(db)

    def get_team_by_project(self, user: User, project_id: UUID) -> TeamResponse:
        team = self.team_repo.get_by_project_id(project_id)
        if not team:
            raise NotFoundError("Team for project", str(project_id))
        return TeamResponse.model_validate(team)

    def add_team_member(self, user: User, team_id: UUID, member_in: TeamMemberCreate) -> TeamMemberResponse:
        team = self.team_repo.get(team_id)
        if not team:
            raise NotFoundError("Team", str(team_id))

        project = self.project_repo.get(team.project_id)
        if not project:
            raise NotFoundError("Project", str(team.project_id))

        if user.role != UserRole.ADMIN:
            org = self.org_repo.get_by_user_id(user.id)
            if not org or project.organization_id != org.id:
                raise ForbiddenError("Only the project owner can manage team members")

        student = self.student_repo.get(member_in.student_id)
        if not student:
            raise NotFoundError("Student", str(member_in.student_id))

        member = self.team_repo.add_member(team_id, student.id, member_in.role_title)
        return TeamMemberResponse.model_validate(member)

    def remove_team_member(self, user: User, team_id: UUID, student_id: UUID) -> None:
        team = self.team_repo.get(team_id)
        if not team:
            raise NotFoundError("Team", str(team_id))

        project = self.project_repo.get(team.project_id)
        if user.role != UserRole.ADMIN:
            org = self.org_repo.get_by_user_id(user.id)
            if not org or project.organization_id != org.id:
                raise ForbiddenError("Only the project owner can manage team members")

        removed = self.team_repo.remove_member(team_id, student_id)
        if not removed:
            raise NotFoundError("Team member not found")
