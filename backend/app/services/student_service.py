from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.student import StudentProfile
from app.schemas.student import (
    StudentProfileUpdate, StudentProfileResponse, StudentProfilePublicResponse,
    StudentSkillCreate, StudentSkillResponse
)
from app.core.errors import NotFoundError, ForbiddenError
from app.repositories.student_repository import StudentRepository
from app.repositories.skill_repository import SkillRepository


class StudentService:
    def __init__(self, db: Session):
        self.db = db
        self.student_repo = StudentRepository(db)
        self.skill_repo = SkillRepository(db)

    def get_profile_by_user(self, user: User) -> StudentProfileResponse:
        profile = self.student_repo.get_by_user_id(user.id)
        if not profile:
            raise NotFoundError("Student profile", str(user.id))
        return StudentProfileResponse.model_validate(profile)

    def get_public_profile(self, profile_id: UUID) -> StudentProfilePublicResponse:
        profile = self.student_repo.get_with_skills(profile_id)
        if not profile:
            raise NotFoundError("Student profile", str(profile_id))
        return StudentProfilePublicResponse.model_validate(profile)

    def update_profile(self, user: User, update_in: StudentProfileUpdate) -> StudentProfileResponse:
        profile = self.student_repo.get_by_user_id(user.id)
        if not profile:
            raise NotFoundError("Student profile", str(user.id))

        updated = self.student_repo.update(profile, update_in)
        self.student_repo.calculate_and_update_completion(updated)
        refreshed = self.student_repo.get_with_skills(updated.id)
        return StudentProfileResponse.model_validate(refreshed)

    def add_skill(self, user: User, skill_in: StudentSkillCreate) -> StudentSkillResponse:
        profile = self.student_repo.get_by_user_id(user.id)
        if not profile:
            raise NotFoundError("Student profile", str(user.id))

        skill = self.skill_repo.get(skill_in.skill_id)
        if not skill:
            raise NotFoundError("Skill", str(skill_in.skill_id))

        student_skill = self.student_repo.add_or_update_skill(
            student_id=profile.id,
            skill_id=skill_in.skill_id,
            proficiency=skill_in.proficiency,
            years_experience=skill_in.years_experience
        )
        return StudentSkillResponse.model_validate(student_skill)

    def remove_skill(self, user: User, skill_id: UUID) -> None:
        profile = self.student_repo.get_by_user_id(user.id)
        if not profile:
            raise NotFoundError("Student profile", str(user.id))

        removed = self.student_repo.remove_skill(profile.id, skill_id)
        if not removed:
            raise NotFoundError("Student skill association not found")
