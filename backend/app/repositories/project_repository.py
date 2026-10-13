from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from app.models.project import Project, ProjectSkill
from app.models.enums import ProjectStatus, DifficultyLevel, SkillImportance, ProficiencyLevel
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: Session):
        super().__init__(Project, db)

    def get_by_slug(self, slug: str) -> Optional[Project]:
        return (
            self.db.query(Project)
            .options(
                joinedload(Project.organization),
                joinedload(Project.skills).joinedload(ProjectSkill.skill)
            )
            .filter(Project.slug == slug)
            .first()
        )

    def get_with_details(self, project_id: UUID) -> Optional[Project]:
        return (
            self.db.query(Project)
            .options(
                joinedload(Project.organization),
                joinedload(Project.skills).joinedload(ProjectSkill.skill),
                joinedload(Project.team),
                joinedload(Project.workspace)
            )
            .filter(Project.id == project_id)
            .first()
        )

    def list_projects(
        self,
        status: Optional[ProjectStatus] = None,
        difficulty: Optional[DifficultyLevel] = None,
        organization_id: Optional[UUID] = None,
        search: Optional[str] = None,
        offset: int = 0,
        limit: int = 20
    ) -> List[Project]:
        query = (
            self.db.query(Project)
            .options(
                joinedload(Project.organization),
                joinedload(Project.skills).joinedload(ProjectSkill.skill)
            )
        )
        if status:
            query = query.filter(Project.status == status)
        if difficulty:
            query = query.filter(Project.difficulty == difficulty)
        if organization_id:
            query = query.filter(Project.organization_id == organization_id)
        if search:
            query = query.filter(
                (Project.title.ilike(f"%{search}%")) | (Project.problem_description.ilike(f"%{search}%"))
            )
        return query.order_by(Project.created_at.desc()).offset(offset).limit(limit).all()

    def count_projects(
        self,
        status: Optional[ProjectStatus] = None,
        difficulty: Optional[DifficultyLevel] = None,
        organization_id: Optional[UUID] = None,
        search: Optional[str] = None
    ) -> int:
        query = self.db.query(Project)
        if status:
            query = query.filter(Project.status == status)
        if difficulty:
            query = query.filter(Project.difficulty == difficulty)
        if organization_id:
            query = query.filter(Project.organization_id == organization_id)
        if search:
            query = query.filter(
                (Project.title.ilike(f"%{search}%")) | (Project.problem_description.ilike(f"%{search}%"))
            )
        return query.count()

    def set_skills(self, project_id: UUID, skills_data: List[dict]) -> None:
        # clear existing project skills
        self.db.query(ProjectSkill).filter(ProjectSkill.project_id == project_id).delete()
        for s in skills_data:
            ps = ProjectSkill(
                project_id=project_id,
                skill_id=s["skill_id"],
                importance=s.get("importance", SkillImportance.REQUIRED),
                minimum_proficiency=s.get("minimum_proficiency")
            )
            self.db.add(ps)
        self.db.commit()

    def update_status(self, project_id: UUID, new_status: ProjectStatus) -> Optional[Project]:
        project = self.get(project_id)
        if project:
            project.status = new_status
            self.db.commit()
            self.db.refresh(project)
        return project
