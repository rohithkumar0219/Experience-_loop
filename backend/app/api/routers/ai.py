from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.enums import AnalysisType
from app.schemas.ai import (
    AIStructureRequest, AIMatchRequest, AIDifficultyRequest,
    AIRequirementRequest, AIProgressRequest, AIEvaluationRequest,
    AIAnalysisResponse
)
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI Assistive Service"])


@router.post("/structure", response_model=AIAnalysisResponse, status_code=status.HTTP_201_CREATED)
def structure_project(
    data_in: AIStructureRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """STRUCTURE: Synthesize raw project problem description into milestones, deliverables, and tech recommendations."""
    service = AIService(db)
    return service.structure_project(data_in.project_id, custom_description=data_in.problem_description)


@router.post("/match", response_model=AIAnalysisResponse, status_code=status.HTTP_201_CREATED)
def match_student(
    data_in: AIMatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """MATCH: Compare candidate student skills and proficiencies against project requirements with assistive scoring."""
    service = AIService(db)
    student_id = data_in.student_id or current_user.id
    return service.match_student(data_in.project_id, student_id)


@router.post("/difficulty", response_model=AIAnalysisResponse, status_code=status.HTTP_201_CREATED)
def estimate_difficulty(
    data_in: AIDifficultyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """DIFFICULTY: Estimate project complexity, difficulty level, and recommended duration."""
    service = AIService(db)
    return service.estimate_difficulty(data_in.project_id)


@router.post("/requirements", response_model=AIAnalysisResponse, status_code=status.HTTP_201_CREATED)
def analyze_requirements(
    data_in: AIRequirementRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """REQUIREMENT: Analyze requirement clarity, identify project risks, and recommend actionable refinements."""
    service = AIService(db)
    return service.analyze_requirements(data_in.project_id)


@router.post("/progress", response_model=AIAnalysisResponse, status_code=status.HTTP_201_CREATED)
def analyze_progress(
    data_in: AIProgressRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """PROGRESS: Analyze workspace task completion metrics, project health, and timeline risks."""
    service = AIService(db)
    return service.analyze_progress(data_in.project_id)


@router.post("/evaluation", response_model=AIAnalysisResponse, status_code=status.HTTP_201_CREATED)
def evaluate_submission(
    data_in: AIEvaluationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """EVALUATION: Assistive review of submission deliverables against project requirements with suggested evaluation rubrics."""
    service = AIService(db)
    return service.evaluate_submission(data_in.project_id, submission_id=data_in.submission_id)


@router.get("/project/{project_id}", response_model=List[AIAnalysisResponse])
def list_project_analyses(
    project_id: UUID,
    analysis_type: Optional[AnalysisType] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List historical AI analyses generated for a project."""
    service = AIService(db)
    return service.list_analyses_for_project(project_id, analysis_type=analysis_type)
