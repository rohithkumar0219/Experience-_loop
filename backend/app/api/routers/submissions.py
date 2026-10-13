from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user, require_student
from app.models.user import User
from app.schemas.submission import (
    SubmissionCreate, SubmissionResponse, SubmissionReview
)
from app.services.submission_service import SubmissionService
from app.services.feedback_service import FeedbackService

router = APIRouter(prefix="/submissions", tags=["Submissions"])


@router.post("/", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
def submit_project(
    sub_in: SubmissionCreate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Submit project deliverables for organization review (Student team member)."""
    service = SubmissionService(db)
    return service.submit_project(current_user, sub_in)


@router.get("/project/{project_id}", response_model=List[SubmissionResponse])
def list_submissions_for_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all submissions for a project."""
    service = SubmissionService(db)
    return service.list_submissions_for_project(current_user, project_id)


@router.get("/{submission_id}", response_model=SubmissionResponse)
def get_submission(
    submission_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get submission details by ID."""
    service = SubmissionService(db)
    return service.get_submission(current_user, submission_id)


@router.patch("/{submission_id}/review", response_model=SubmissionResponse)
def review_submission(
    submission_id: UUID,
    review_in: SubmissionReview,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Review a submission (UNDER_REVIEW, CHANGES_REQUESTED, APPROVED, REJECTED) - Organization or Admin."""
    service = FeedbackService(db)
    return service.review_submission(current_user, submission_id, review_in)
