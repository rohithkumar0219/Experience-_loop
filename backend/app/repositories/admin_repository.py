from datetime import datetime, timezone
from typing import Optional, List, Any
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.admin import Report, AuditLog
from app.models.enums import ReportStatus, ProjectStatus, VerificationStatus, OrganizationVerificationStatus
from app.models.user import User
from app.models.student import StudentProfile
from app.models.organization import Organization
from app.models.project import Project
from app.models.application import Application
from app.models.experience import ExperienceRecord
from app.repositories.base import BaseRepository


class AdminRepository:
    def __init__(self, db: Session):
        self.db = db

    # --- Reports ---
    def list_reports(
        self,
        status: Optional[ReportStatus] = None,
        entity_type: Optional[str] = None,
        offset: int = 0,
        limit: int = 50
    ) -> List[Report]:
        query = self.db.query(Report)
        if status:
            query = query.filter(Report.status == status)
        if entity_type:
            query = query.filter(Report.entity_type == entity_type)
        return query.order_by(Report.status.asc()).offset(offset).limit(limit).all()

    def count_reports(self, status: Optional[ReportStatus] = None) -> int:
        query = self.db.query(Report)
        if status:
            query = query.filter(Report.status == status)
        return query.count()

    def get_report(self, report_id: UUID) -> Optional[Report]:
        return self.db.query(Report).filter(Report.id == report_id).first()

    def create_report(self, data: dict) -> Report:
        r = Report(**data)
        self.db.add(r)
        self.db.commit()
        self.db.refresh(r)
        return r

    def update_report_status(self, report_id: UUID, status: ReportStatus, admin_id: UUID) -> Optional[Report]:
        r = self.get_report(report_id)
        if r:
            r.status = status
            r.resolved_by = admin_id
            r.resolved_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(r)
        return r

    # --- Audit Logs ---
    def create_audit_log(
        self,
        action: str,
        entity_type: str,
        entity_id: Optional[UUID] = None,
        actor_user_id: Optional[UUID] = None,
        old_values: Optional[Any] = None,
        new_values: Optional[Any] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        log = AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_user_id=actor_user_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def list_audit_logs(
        self,
        entity_type: Optional[str] = None,
        actor_user_id: Optional[UUID] = None,
        action: Optional[str] = None,
        offset: int = 0,
        limit: int = 50
    ) -> List[AuditLog]:
        query = self.db.query(AuditLog)
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        if actor_user_id:
            query = query.filter(AuditLog.actor_user_id == actor_user_id)
        if action:
            query = query.filter(AuditLog.action.ilike(f"%{action}%"))
        return query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()

    def count_audit_logs(self, entity_type: Optional[str] = None) -> int:
        query = self.db.query(AuditLog)
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        return query.count()

    # --- Dashboard Stats ---
    def get_dashboard_stats(self) -> dict:
        total_users = self.db.query(User).count()
        total_students = self.db.query(StudentProfile).count()
        total_organizations = self.db.query(Organization).count()
        total_projects = self.db.query(Project).count()
        active_projects = self.db.query(Project).filter(
            Project.status.in_([ProjectStatus.APPLICATIONS_OPEN, ProjectStatus.SELECTION, ProjectStatus.IN_PROGRESS])
        ).count()
        completed_projects = self.db.query(Project).filter(
            Project.status.in_([ProjectStatus.COMPLETED, ProjectStatus.VERIFIED])
        ).count()
        total_applications = self.db.query(Application).count()
        verified_experiences = self.db.query(ExperienceRecord).filter(
            ExperienceRecord.verification_status == VerificationStatus.VERIFIED
        ).count()
        open_reports = self.db.query(Report).filter(Report.status == ReportStatus.OPEN).count()

        return {
            "total_users": total_users,
            "total_students": total_students,
            "total_organizations": total_organizations,
            "total_projects": total_projects,
            "active_projects": active_projects,
            "completed_projects": completed_projects,
            "total_applications": total_applications,
            "verified_experiences": verified_experiences,
            "open_reports": open_reports,
        }
