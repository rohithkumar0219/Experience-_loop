from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user, require_student
from app.models.user import User
from app.schemas.student import (
    StudentProfileResponse, StudentProfilePublicResponse, StudentProfileUpdate,
    StudentSkillCreate, StudentSkillResponse
)
from app.schemas.common import MessageResponse
from app.services.student_service import StudentService

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/me", response_model=StudentProfileResponse)
def get_my_student_profile(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Retrieve the current logged-in student's complete profile with skills and completion score."""
    service = StudentService(db)
    return service.get_profile_by_user(current_user)


@router.put("/me", response_model=StudentProfileResponse)
def update_my_student_profile(
    profile_in: StudentProfileUpdate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Update student profile details and dynamically recalculate profile completion score (0-100)."""
    service = StudentService(db)
    return service.update_profile(current_user, profile_in)


@router.post("/me/skills", response_model=StudentSkillResponse, status_code=status.HTTP_201_CREATED)
def add_or_update_my_skill(
    skill_in: StudentSkillCreate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Add or update a skill with proficiency level and years of experience on the student profile."""
    service = StudentService(db)
    return service.add_skill(current_user, skill_in)


@router.delete("/me/skills/{skill_id}", response_model=MessageResponse)
def remove_my_skill(
    skill_id: UUID,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Remove a skill from the student profile."""
    service = StudentService(db)
    service.remove_skill(current_user, skill_id)
    return MessageResponse(message="Skill successfully removed from profile")


@router.get("/{student_id}", response_model=StudentProfilePublicResponse)
def get_public_student_profile(
    student_id: UUID,
    db: Session = Depends(get_db)
):
    """Publicly view a student's portfolio profile."""
    service = StudentService(db)
    return service.get_public_profile(student_id)
