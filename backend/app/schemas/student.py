from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import ProficiencyLevel
from app.schemas.skill import SkillResponse


class StudentSkillBase(BaseModel):
    skill_id: UUID
    proficiency: ProficiencyLevel
    years_experience: Decimal = Field(default=Decimal("0.0"), ge=0, le=50)


class StudentSkillCreate(StudentSkillBase):
    pass


class StudentSkillUpdate(BaseModel):
    proficiency: Optional[ProficiencyLevel] = None
    years_experience: Optional[Decimal] = Field(None, ge=0, le=50)


class StudentSkillResponse(BaseModel):
    skill_id: UUID
    proficiency: ProficiencyLevel
    years_experience: Decimal
    skill: Optional[SkillResponse] = None

    model_config = ConfigDict(from_attributes=True)


class StudentProfileBase(BaseModel):
    full_name: str = Field(..., max_length=150)
    headline: Optional[str] = Field(None, max_length=200)
    bio: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=30)
    profile_photo_url: Optional[str] = None
    college: Optional[str] = Field(None, max_length=200)
    degree: Optional[str] = Field(None, max_length=150)
    graduation_year: Optional[int] = Field(None, ge=1970, le=2100)
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    linkedin_url: Optional[str] = None


class StudentProfileCreate(StudentProfileBase):
    pass


class StudentProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=150)
    headline: Optional[str] = Field(None, max_length=200)
    bio: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=30)
    profile_photo_url: Optional[str] = None
    college: Optional[str] = Field(None, max_length=200)
    degree: Optional[str] = Field(None, max_length=150)
    graduation_year: Optional[int] = Field(None, ge=1970, le=2100)
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    linkedin_url: Optional[str] = None


class StudentProfileResponse(StudentProfileBase):
    id: UUID
    user_id: UUID
    profile_completion: int
    skills: List[StudentSkillResponse] = []

    model_config = ConfigDict(from_attributes=True)


class StudentProfilePublicResponse(BaseModel):
    id: UUID
    full_name: str
    headline: Optional[str] = None
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    graduation_year: Optional[int] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    profile_completion: int
    skills: List[StudentSkillResponse] = []

    model_config = ConfigDict(from_attributes=True)
