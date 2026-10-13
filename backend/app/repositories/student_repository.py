from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from app.models.student import StudentProfile, StudentSkill
from app.models.enums import ProficiencyLevel
from app.repositories.base import BaseRepository


class StudentRepository(BaseRepository[StudentProfile]):
    def __init__(self, db: Session):
        super().__init__(StudentProfile, db)

    def get_by_user_id(self, user_id: UUID) -> Optional[StudentProfile]:
        return (
            self.db.query(StudentProfile)
            .options(joinedload(StudentProfile.skills).joinedload(StudentSkill.skill))
            .filter(StudentProfile.user_id == user_id)
            .first()
        )

    def get_with_skills(self, profile_id: UUID) -> Optional[StudentProfile]:
        return (
            self.db.query(StudentProfile)
            .options(joinedload(StudentProfile.skills).joinedload(StudentSkill.skill))
            .filter(StudentProfile.id == profile_id)
            .first()
        )

    def calculate_and_update_completion(self, profile: StudentProfile) -> int:
        """Calculate profile completion percentage from 0 to 100 based on filled fields."""
        fields_to_check = [
            bool(profile.full_name),
            bool(profile.headline),
            bool(profile.bio),
            bool(profile.phone),
            bool(profile.profile_photo_url),
            bool(profile.college),
            bool(profile.degree),
            bool(profile.graduation_year),
            bool(profile.github_url or profile.portfolio_url or profile.linkedin_url),
            len(profile.skills) > 0,
        ]
        score = int((sum(1 for f in fields_to_check if f) / len(fields_to_check)) * 100)
        profile.profile_completion = min(100, max(0, score))
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile.profile_completion

    def add_or_update_skill(
        self,
        student_id: UUID,
        skill_id: UUID,
        proficiency: ProficiencyLevel,
        years_experience: Decimal = Decimal("0.0")
    ) -> StudentSkill:
        student_skill = (
            self.db.query(StudentSkill)
            .filter(StudentSkill.student_id == student_id, StudentSkill.skill_id == skill_id)
            .first()
        )
        if student_skill:
            student_skill.proficiency = proficiency
            student_skill.years_experience = years_experience
        else:
            student_skill = StudentSkill(
                student_id=student_id,
                skill_id=skill_id,
                proficiency=proficiency,
                years_experience=years_experience,
            )
            self.db.add(student_skill)
        self.db.commit()
        self.db.refresh(student_skill)

        # recalculate completion
        profile = self.get(student_id)
        if profile:
            self.calculate_and_update_completion(profile)

        return student_skill

    def remove_skill(self, student_id: UUID, skill_id: UUID) -> bool:
        student_skill = (
            self.db.query(StudentSkill)
            .filter(StudentSkill.student_id == student_id, StudentSkill.skill_id == skill_id)
            .first()
        )
        if student_skill:
            self.db.delete(student_skill)
            self.db.commit()
            profile = self.get(student_id)
            if profile:
                self.calculate_and_update_completion(profile)
            return True
        return False
