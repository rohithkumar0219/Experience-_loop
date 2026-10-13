from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.skill import Skill
from app.schemas.skill import SkillCreate, SkillUpdate, SkillResponse
from app.schemas.common import PaginatedResponse
from app.core.errors import NotFoundError, ConflictError
from app.repositories.skill_repository import SkillRepository


class SkillService:
    def __init__(self, db: Session):
        self.db = db
        self.skill_repo = SkillRepository(db)

    def list_skills(
        self,
        query_str: Optional[str] = None,
        category: Optional[str] = None,
        page: int = 1,
        per_page: int = 50
    ) -> PaginatedResponse[SkillResponse]:
        offset = (page - 1) * per_page
        items = self.skill_repo.search_skills(query_str=query_str, category=category, offset=offset, limit=per_page)
        total = self.skill_repo.count_skills(query_str=query_str, category=category)
        total_pages = (total + per_page - 1) // per_page if total > 0 else 1

        return PaginatedResponse(
            items=[SkillResponse.model_validate(s) for s in items],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )

    def get_skill(self, skill_id: UUID) -> SkillResponse:
        skill = self.skill_repo.get(skill_id)
        if not skill:
            raise NotFoundError("Skill", str(skill_id))
        return SkillResponse.model_validate(skill)

    def create_skill(self, skill_in: SkillCreate) -> SkillResponse:
        existing = self.skill_repo.get_by_name(skill_in.name)
        if existing:
            raise ConflictError(f"Skill '{skill_in.name}' already exists")
        skill = self.skill_repo.create(skill_in)
        return SkillResponse.model_validate(skill)

    def update_skill(self, skill_id: UUID, skill_in: SkillUpdate) -> SkillResponse:
        skill = self.skill_repo.get(skill_id)
        if not skill:
            raise NotFoundError("Skill", str(skill_id))
        if skill_in.name and skill_in.name.lower() != skill.name.lower():
            existing = self.skill_repo.get_by_name(skill_in.name)
            if existing:
                raise ConflictError(f"Skill '{skill_in.name}' already exists")
        updated = self.skill_repo.update(skill, skill_in)
        return SkillResponse.model_validate(updated)
