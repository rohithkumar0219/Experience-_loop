from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.skill import Skill
from app.repositories.base import BaseRepository


class SkillRepository(BaseRepository[Skill]):
    def __init__(self, db: Session):
        super().__init__(Skill, db)

    def get_by_name(self, name: str) -> Optional[Skill]:
        return self.db.query(Skill).filter(Skill.name.ilike(name.strip())).first()

    def search_skills(self, query_str: Optional[str] = None, category: Optional[str] = None, offset: int = 0, limit: int = 50) -> List[Skill]:
        query = self.db.query(Skill)
        if query_str:
            query = query.filter(Skill.name.ilike(f"%{query_str.strip()}%"))
        if category:
            query = query.filter(Skill.category.ilike(category.strip()))
        return query.order_by(Skill.name.asc()).offset(offset).limit(limit).all()

    def count_skills(self, query_str: Optional[str] = None, category: Optional[str] = None) -> int:
        query = self.db.query(Skill)
        if query_str:
            query = query.filter(Skill.name.ilike(f"%{query_str.strip()}%"))
        if category:
            query = query.filter(Skill.category.ilike(category.strip()))
        return query.count()
