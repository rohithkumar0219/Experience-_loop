from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user, require_org_or_admin
from app.models.user import User
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.services.feedback_service import FeedbackService

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback_and_complete_project(
    feedback_in: FeedbackCreate,
    current_user: User = Depends(require_org_or_admin),
    db: Session = Depends(get_db)
):
    """Submit project evaluation feedback (0-5 ratings for technical implementation, requirement fulfillment,
    communication, problem solving, overall rating).
    Automatically approves submission, marks project VERIFIED, and generates Experience Records for team members.
    """
    service = FeedbackService(db)
    return service.submit_feedback_and_complete(current_user, feedback_in)


@router.get("/project/{project_id}", response_model=List[FeedbackResponse])
def list_feedback_for_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List evaluation feedback entries for a project."""
    service = FeedbackService(db)
    return service.list_feedback_for_project(project_id)
