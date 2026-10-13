from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.team import TeamResponse, TeamMemberCreate, TeamMemberResponse
from app.services.team_service import TeamService

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get("/project/{project_id}", response_model=TeamResponse)
def get_team_for_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve the project team and its members."""
    service = TeamService(db)
    return service.get_team_by_project(current_user, project_id)


@router.post("/{team_id}/members", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
def add_team_member(
    team_id: UUID,
    member_in: TeamMemberCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a student member to the team (Project Organization or Admin)."""
    service = TeamService(db)
    return service.add_team_member(current_user, team_id, member_in)


@router.delete("/{team_id}/members/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_team_member(
    team_id: UUID,
    student_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a student member from the team (Project Organization or Admin)."""
    service = TeamService(db)
    service.remove_team_member(current_user, team_id, student_id)
    return None
