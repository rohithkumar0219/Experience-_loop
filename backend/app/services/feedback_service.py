import re
import uuid
from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.feedback import Feedback
from app.models.submission import Submission
from app.models.project import Project, ProjectSkill
from app.models.experience import ExperienceRecord
from app.models.enums import SubmissionStatus, ProjectStatus, VerificationStatus, UserRole
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate, FeedbackResponse
from app.schemas.submission import SubmissionReview, SubmissionResponse
from app.core.errors import NotFoundError, ForbiddenError, BadRequestError
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.submission_repository import SubmissionRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.team_repository import TeamRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.experience_repository import ExperienceRepository
from app.repositories.admin_repository import AdminRepository
from app.services.notification_service import NotificationService


def generate_experience_slug(student_name: str, project_title: str) -> str:
    s_clean = re.sub(r"[^\w\s-]", "", student_name.lower().strip())
    s_slug = re.sub(r"[-\s]+", "-", s_clean)[:20]
    p_clean = re.sub(r"[^\w\s-]", "", project_title.lower().strip())
    p_slug = re.sub(r"[-\s]+", "-", p_clean)[:30]
    rand_suffix = uuid.uuid4().hex[:8]
    return f"exp-{s_slug}-{p_slug}-{rand_suffix}"


class FeedbackService:
    def __init__(self, db: Session):
        self.db = db
        self.feedback_repo = FeedbackRepository(db)
        self.sub_repo = SubmissionRepository(db)
        self.project_repo = ProjectRepository(db)
        self.org_repo = OrganizationRepository(db)
        self.team_repo = TeamRepository(db)
        self.student_repo = StudentRepository(db)
        self.exp_repo = ExperienceRepository(db)
        self.admin_repo = AdminRepository(db)

    def review_submission(
        self,
        user: User,
        submission_id: UUID,
        review_in: SubmissionReview
    ) -> SubmissionResponse:
        submission = self.sub_repo.get(submission_id)
        if not submission:
            raise NotFoundError("Submission", str(submission_id))

        project = self.project_repo.get(submission.project_id)
        if not project:
            raise NotFoundError("Project", str(submission.project_id))

        if user.role != UserRole.ADMIN:
            org = self.org_repo.get_by_user_id(user.id)
            if not org or project.organization_id != org.id:
                raise ForbiddenError("Only the project organization can review submissions")

        submission.status = review_in.status
        submission.reviewed_at = datetime.now(timezone.utc)
        if review_in.notes:
            submission.notes = (submission.notes or "") + f"\n[Review Note]: {review_in.notes}"

        if review_in.status == SubmissionStatus.UNDER_REVIEW:
            project.status = ProjectStatus.UNDER_REVIEW
        elif review_in.status == SubmissionStatus.CHANGES_REQUESTED:
            project.status = ProjectStatus.IN_PROGRESS
        elif review_in.status == SubmissionStatus.APPROVED:
            project.status = ProjectStatus.COMPLETED

        self.db.commit()
        self.db.refresh(submission)

        # Notify submitter
        NotificationService.send_notification(
            db=self.db,
            user_id=submission.submitted_by,
            notif_type="SUBMISSION_REVIEWED",
            title=f"Submission {review_in.status.value.replace('_', ' ').title()}",
            message=f"Your submission for project '{project.title}' is now: {review_in.status.value}",
            entity_type="submission",
            entity_id=submission.id
        )

        return SubmissionResponse.model_validate(submission)

    def submit_feedback_and_complete(
        self,
        user: User,
        feedback_in: FeedbackCreate
    ) -> FeedbackResponse:
        project = self.project_repo.get_with_details(feedback_in.project_id)
        if not project:
            raise NotFoundError("Project", str(feedback_in.project_id))

        if user.role != UserRole.ADMIN:
            org = self.org_repo.get_by_user_id(user.id)
            if not org or project.organization_id != org.id:
                raise ForbiddenError("Only the organization owner can submit validation feedback")
        else:
            org = self.org_repo.get(project.organization_id)

        # Create Feedback record
        fb_data = feedback_in.model_dump()
        fb_data["organization_id"] = org.id
        fb_data["created_at"] = datetime.now(timezone.utc)

        feedback = self.feedback_repo.create(fb_data)

        # Mark project as VERIFIED/COMPLETED
        project.status = ProjectStatus.VERIFIED
        project.updated_at = datetime.now(timezone.utc)

        # If submission was linked, mark it approved
        if feedback_in.submission_id:
            sub = self.sub_repo.get(feedback_in.submission_id)
            if sub:
                sub.status = SubmissionStatus.APPROVED
                sub.reviewed_at = datetime.now(timezone.utc)

        # Create Experience Records for all team members
        team = self.team_repo.get_by_project_id(project.id)
        students_to_award = []

        if feedback_in.student_id:
            # Award to specific student
            student = self.student_repo.get(feedback_in.student_id)
            if student:
                students_to_award.append((student, "Project Contributor"))
        elif team and team.members:
            for member in team.members:
                students_to_award.append((member.student, member.role_title or "Project Contributor"))

        tech_list = [ps.skill.name for ps in project.skills if ps.skill] if project.skills else []

        for student, role in students_to_award:
            if not student:
                continue

            # Check if experience record already exists
            existing_exp = self.exp_repo.get_by_project_and_student(project.id, student.id)
            if not existing_exp:
                slug = generate_experience_slug(student.full_name, project.title)
                exp_record = ExperienceRecord(
                    project_id=project.id,
                    student_id=student.id,
                    team_id=team.id if team else None,
                    role_title=role,
                    problem_solved=project.problem_description,
                    technologies=tech_list,
                    deliverables=project.deliverables,
                    duration_days=project.estimated_duration_days,
                    outcome=feedback_in.comments or "Project deliverables successfully verified by organization.",
                    organization_feedback_id=feedback.id,
                    verification_status=VerificationStatus.VERIFIED,
                    verified_at=datetime.now(timezone.utc),
                    public_slug=slug
                )
                self.db.add(exp_record)
                self.db.flush()

                # Notify student of verified experience
                if student.user_id:
                    NotificationService.send_notification(
                        db=self.db,
                        user_id=student.user_id,
                        notif_type="EXPERIENCE_VERIFIED",
                        title="Verified Experience Record Issued!",
                        message=f"Your work on '{project.title}' has been reviewed and verified by {org.name}.",
                        entity_type="experience",
                        entity_id=exp_record.id
                    )

        self.db.commit()
        self.db.refresh(feedback)

        # Audit log
        self.admin_repo.create_audit_log(
            action="PROJECT_COMPLETED_AND_VERIFIED",
            entity_type="project",
            entity_id=project.id,
            actor_user_id=user.id,
            new_values={"feedback_id": str(feedback.id), "status": project.status.value}
        )

        return FeedbackResponse.model_validate(feedback)

    def list_feedback_for_project(self, project_id: UUID) -> List[FeedbackResponse]:
        items = self.feedback_repo.list_by_project(project_id)
        return [FeedbackResponse.model_validate(f) for f in items]
