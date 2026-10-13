import re
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.student import StudentProfile
from app.models.organization import Organization
from app.models.enums import UserRole, OrganizationVerificationStatus
from app.schemas.user import UserCreate, UserLogin, TokenResponse, UserResponse
from app.core.security import hash_password, verify_password, create_access_token
from app.core.errors import ConflictError, UnauthorizedError, BadRequestError
from app.repositories.user_repository import UserRepository


def generate_slug(text: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", text.lower().strip())
    slug = re.sub(r"[-\s]+", "-", cleaned)
    return slug or "org"


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register(self, user_in: UserCreate) -> TokenResponse:
        # Check if email is already registered
        existing_user = self.user_repo.get_by_email(user_in.email)
        if existing_user:
            raise ConflictError("A user with this email address already exists")

        # Create user record
        hashed_pwd = hash_password(user_in.password)
        user = User(
            email=user_in.email,
            password_hash=hashed_pwd,
            role=user_in.role,
            is_active=True,
            is_verified=False
        )
        self.db.add(user)
        self.db.flush()

        # Create associated role profile
        if user_in.role == UserRole.STUDENT:
            name = user_in.full_name or user_in.email.split("@")[0].title()
            student_profile = StudentProfile(
                user_id=user.id,
                full_name=name,
                profile_completion=10
            )
            self.db.add(student_profile)
        elif user_in.role == UserRole.ORGANIZATION:
            org_name = user_in.organization_name or user_in.full_name or "My Organization"
            base_slug = generate_slug(org_name)
            # Ensure unique slug
            slug = base_slug
            counter = 1
            while self.db.query(Organization).filter(Organization.slug == slug).first():
                slug = f"{base_slug}-{counter}"
                counter += 1

            organization = Organization(
                user_id=user.id,
                name=org_name,
                slug=slug,
                verification_status=OrganizationVerificationStatus.PENDING
            )
            self.db.add(organization)

        self.db.commit()
        self.db.refresh(user)

        # Generate JWT token
        token = create_access_token(subject=str(user.id))
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )

    def login(self, login_in: UserLogin) -> TokenResponse:
        user = self.user_repo.get_by_email(login_in.email)
        if not user or not verify_password(login_in.password, user.password_hash):
            raise UnauthorizedError("Incorrect email or password")

        if not user.is_active:
            raise UnauthorizedError("User account is inactive. Please contact support.")

        # Update last login timestamp
        self.user_repo.update_last_login(user.id)

        token = create_access_token(subject=str(user.id))
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )
