from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import require_admin, get_current_user
from app.models.user import User
from app.schemas.skill import SkillCreate, SkillUpdate, SkillResponse
from app.schemas.common import PaginatedResponse
from app.services.skill_service import SkillService

router = APIRouter(prefix="/skills", tags=["Skills"])


@router.get("/", response_model=PaginatedResponse[SkillResponse])
def list_skills(
    query: Optional[str] = None,
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List or search platform skills by name or category."""
    service = SkillService(db)
    return service.list_skills(query_str=query, category=category, page=page, per_page=per_page)


@router.get("/{skill_id}", response_model=SkillResponse)
def get_skill(skill_id: UUID, db: Session = Depends(get_db)):
    """Retrieve details for a single skill."""
    service = SkillService(db)
    return service.get_skill(skill_id)


@router.post("/", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
def create_skill(
    skill_in: SkillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new skill in the global catalog."""
    service = SkillService(db)
    return service.create_skill(skill_in)


@router.put("/{skill_id}", response_model=SkillResponse)
def update_skill(
    skill_id: UUID,
    skill_in: SkillUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update skill name or category (Admin only)."""
    service = SkillService(db)
    return service.update_skill(skill_id, skill_in)
