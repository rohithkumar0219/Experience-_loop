from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import OrganizationVerificationStatus


class OrganizationBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    website_url: Optional[str] = None
    logo_url: Optional[str] = None
    industry: Optional[str] = Field(None, max_length=120)
    location: Optional[str] = Field(None, max_length=200)


class OrganizationCreate(OrganizationBase):
    slug: Optional[str] = Field(None, max_length=220)


class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    website_url: Optional[str] = None
    logo_url: Optional[str] = None
    industry: Optional[str] = Field(None, max_length=120)
    location: Optional[str] = Field(None, max_length=200)


class OrganizationVerificationUpdate(BaseModel):
    verification_status: OrganizationVerificationStatus


class OrganizationResponse(OrganizationBase):
    id: UUID
    user_id: UUID
    slug: str
    verification_status: OrganizationVerificationStatus
    verified_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class OrganizationPublicResponse(OrganizationBase):
    id: UUID
    slug: str
    verification_status: OrganizationVerificationStatus

    model_config = ConfigDict(from_attributes=True)
