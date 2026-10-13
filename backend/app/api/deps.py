from typing import Generator, List, Callable
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_access_token
from app.core.errors import UnauthorizedError, ForbiddenError
from app.models.user import User
from app.models.enums import UserRole
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """Dependency that extracts and validates the current authenticated user."""
    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        raise UnauthorizedError("Invalid or expired authentication token")

    user_id_str = payload.get("sub")
    try:
        user_id = UUID(user_id_str)
    except (ValueError, TypeError):
        raise UnauthorizedError("Malformed authentication subject")

    user_repo = UserRepository(db)
    user = user_repo.get(user_id)
    if not user:
        raise UnauthorizedError("User does not exist")

    if not user.is_active:
        raise ForbiddenError("User account is inactive")

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    return current_user


def require_roles(*allowed_roles: UserRole) -> Callable:
    """Dependency factory for Role-Based Access Control."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise ForbiddenError(f"Access restricted to roles: {[r.value for r in allowed_roles]}")
        return current_user
    return role_checker


# Convenient role-specific dependencies
require_student = require_roles(UserRole.STUDENT)
require_organization = require_roles(UserRole.ORGANIZATION)
require_admin = require_roles(UserRole.ADMIN)
require_org_or_admin = require_roles(UserRole.ORGANIZATION, UserRole.ADMIN)
require_authenticated = Depends(get_current_active_user)
