from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from app.models.team import Team, TeamMember
from app.repositories.base import BaseRepository


class TeamRepository(BaseRepository[Team]):
    def __init__(self, db: Session):
        super().__init__(Team, db)

    def get_by_project_id(self, project_id: UUID) -> Optional[Team]:
        return (
            self.db.query(Team)
            .options(
                joinedload(Team.members).joinedload(TeamMember.student)
            )
            .filter(Team.project_id == project_id)
            .first()
        )

    def add_member(self, team_id: UUID, student_id: UUID, role_title: Optional[str] = None) -> TeamMember:
        member = (
            self.db.query(TeamMember)
            .filter(TeamMember.team_id == team_id, TeamMember.student_id == student_id)
            .first()
        )
        if member:
            if role_title:
                member.role_title = role_title
        else:
            member = TeamMember(
                team_id=team_id,
                student_id=student_id,
                role_title=role_title,
                joined_at=datetime.now(timezone.utc)
            )
            self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member

    def remove_member(self, team_id: UUID, student_id: UUID) -> bool:
        member = (
            self.db.query(TeamMember)
            .filter(TeamMember.team_id == team_id, TeamMember.student_id == student_id)
            .first()
        )
        if member:
            self.db.delete(member)
            self.db.commit()
            return True
        return False
