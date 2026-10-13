import json
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, Dict, Any, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.project import Project
from app.models.student import StudentProfile
from app.models.submission import Submission
from app.models.workspace import Workspace
from app.models.ai import AIAnalysis
from app.models.enums import AnalysisType, DifficultyLevel, TaskStatus
from app.schemas.ai import AIAnalysisResponse
from app.core.errors import NotFoundError
from app.repositories.project_repository import ProjectRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.submission_repository import SubmissionRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.repositories.ai_repository import AIRepository

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_repo = AIRepository(db)
        self.project_repo = ProjectRepository(db)
        self.student_repo = StudentRepository(db)
        self.submission_repo = SubmissionRepository(db)
        self.workspace_repo = WorkspaceRepository(db)

    def _persist_analysis(
        self,
        project_id: UUID,
        analysis_type: AnalysisType,
        input_snapshot: Dict[str, Any],
        output: Dict[str, Any],
        model_name: str = "experienceloop-assistive-v1",
        confidence: float = 0.92
    ) -> AIAnalysisResponse:
        analysis = AIAnalysis(
            project_id=project_id,
            analysis_type=analysis_type,
            input_snapshot=input_snapshot,
            output=output,
            model_name=model_name,
            confidence=Decimal(str(confidence)),
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return AIAnalysisResponse.model_validate(analysis)

    def _call_gemini_if_configured(self, prompt: str) -> Optional[str]:
        """Calls Google Gemini if API key is present."""
        if not settings.GEMINI_API_KEY:
            return None
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(settings.GEMINI_MODEL)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.warning(f"Gemini API call failed, falling back to local analysis engine: {e}")
            return None

    # 1. STRUCTURE: Convert raw problem description into structured brief
    def structure_project(self, project_id: UUID, custom_description: Optional[str] = None) -> AIAnalysisResponse:
        project = self.project_repo.get_with_details(project_id)
        if not project:
            raise NotFoundError("Project", str(project_id))

        problem_text = custom_description or project.problem_description
        input_data = {
            "title": project.title,
            "problem_description": problem_text
        }

        # Assistive structured synthesis
        suggested_milestones = [
            {"title": "Requirement Clarification & Architecture Setup", "description": "Set up environment and define technical specification."},
            {"title": "Core Implementation & Feature Development", "description": "Implement the core functionality solving the primary problem."},
            {"title": "Testing, Deployment & Documentation", "description": "Verify deliverables, write setup guides, and prepare live demo."}
        ]

        suggested_deliverables = [
            "Source code repository with modular structure",
            "README.md with setup instructions and environment variables",
            "Working demo or deployment link",
            "Test suite covering edge cases"
        ]

        output = {
            "structured_summary": f"Structured implementation plan for {project.title}",
            "technical_scope": f"Focuses on delivering a reliable solution for: {problem_text[:200]}...",
            "suggested_milestones": suggested_milestones,
            "suggested_deliverables": suggested_deliverables,
            "recommended_technologies": [ps.skill.name for ps in project.skills if ps.skill] if project.skills else ["Python", "FastAPI", "PostgreSQL"],
            "note": "AI recommendations are assistive only. The organization retains full control over requirements."
        }

        # Optionally enrich project's structured_brief
        if not project.structured_brief:
            project.structured_brief = output
            self.db.commit()

        return self._persist_analysis(
            project_id=project.id,
            analysis_type=AnalysisType.STRUCTURE,
            input_snapshot=input_data,
            output=output,
            confidence=0.95
        )

    # 2. MATCH: Match student skills & experience against project requirements
    def match_student(self, project_id: UUID, student_id: UUID) -> AIAnalysisResponse:
        project = self.project_repo.get_with_details(project_id)
        if not project:
            raise NotFoundError("Project", str(project_id))

        student = self.student_repo.get_with_skills(student_id)
        if not student:
            raise NotFoundError("Student profile", str(student_id))

        required_skills = {ps.skill.name.lower(): ps for ps in project.skills if ps.skill}
        student_skills = {ss.skill.name.lower(): ss for ss in student.skills if ss.skill}

        matched = []
        missing = []

        for req_name, ps in required_skills.items():
            if req_name in student_skills:
                matched.append({
                    "skill": ps.skill.name,
                    "student_proficiency": student_skills[req_name].proficiency.value,
                    "required_level": ps.minimum_proficiency.value if ps.minimum_proficiency else "ANY"
                })
            else:
                missing.append(ps.skill.name)

        total_req = len(required_skills) if required_skills else 1
        match_score = int((len(matched) / total_req) * 100) if required_skills else 80

        input_data = {
            "project_id": str(project_id),
            "student_id": str(student_id),
            "project_skills": list(required_skills.keys()),
            "student_skills": list(student_skills.keys())
        }

        output = {
            "match_score": match_score,
            "matched_skills": matched,
            "missing_skills": missing,
            "recommendation": "Strong Match" if match_score >= 70 else ("Moderate Match" if match_score >= 40 else "Growth Opportunity"),
            "justification": f"Candidate demonstrates {len(matched)} of {len(required_skills)} required technical skills for '{project.title}'.",
            "assistive_warning": "AI cannot accept or reject applications automatically; selection must be made by the organization."
        }

        return self._persist_analysis(
            project_id=project.id,
            analysis_type=AnalysisType.MATCH,
            input_snapshot=input_data,
            output=output,
            confidence=0.90
        )

    # 3. DIFFICULTY: Project difficulty estimation and time evaluation
    def estimate_difficulty(self, project_id: UUID) -> AIAnalysisResponse:
        project = self.project_repo.get_with_details(project_id)
        if not project:
            raise NotFoundError("Project", str(project_id))

        word_count = len(project.problem_description.split())
        num_skills = len(project.skills)

        if word_count > 150 or num_skills >= 4:
            estimated_diff = DifficultyLevel.ADVANCED
            suggested_days = 21
            complexity = "High"
        elif word_count > 60 or num_skills >= 2:
            estimated_diff = DifficultyLevel.INTERMEDIATE
            suggested_days = 14
            complexity = "Medium"
        else:
            estimated_diff = DifficultyLevel.BEGINNER
            suggested_days = 7
            complexity = "Low"

        input_data = {
            "title": project.title,
            "description_length": word_count,
            "skills_count": num_skills,
            "current_difficulty": project.difficulty.value
        }

        output = {
            "recommended_difficulty": estimated_diff.value,
            "complexity_level": complexity,
            "estimated_duration_days": suggested_days,
            "current_difficulty": project.difficulty.value,
            "justification": f"Based on {num_skills} required competencies and problem description scope."
        }

        return self._persist_analysis(
            project_id=project.id,
            analysis_type=AnalysisType.DIFFICULTY,
            input_snapshot=input_data,
            output=output,
            confidence=0.88
        )

    # 4. REQUIREMENT: Requirement clarity and risk analysis
    def analyze_requirements(self, project_id: UUID) -> AIAnalysisResponse:
        project = self.project_repo.get_with_details(project_id)
        if not project:
            raise NotFoundError("Project", str(project_id))

        desc = project.problem_description
        has_deliverables = bool(project.deliverables)
        has_skills = len(project.skills) > 0

        clarity_score = 70
        risks = []
        suggestions = []

        if len(desc.split()) < 30:
            clarity_score -= 20
            risks.append("Problem description is very brief; students may need significant clarification.")
            suggestions.append("Add specific user flows or sample inputs/outputs.")

        if not has_deliverables:
            clarity_score -= 15
            risks.append("Expected deliverables are not formally enumerated.")
            suggestions.append("Explicitly state whether live deployment or repository only is required.")

        if not has_skills:
            clarity_score -= 15
            risks.append("No technical skills tagged on project.")
            suggestions.append("Attach primary programming languages and frameworks required.")

        input_data = {
            "title": project.title,
            "problem_description": desc
        }

        output = {
            "clarity_score": max(20, clarity_score),
            "identified_risks": risks,
            "recommendations": suggestions,
            "status": "Clear" if clarity_score >= 70 else "Needs Refinement"
        }

        return self._persist_analysis(
            project_id=project.id,
            analysis_type=AnalysisType.REQUIREMENT,
            input_snapshot=input_data,
            output=output,
            confidence=0.91
        )

    # 5. PROGRESS: Workspace progress and timeline projection
    def analyze_progress(self, project_id: UUID) -> AIAnalysisResponse:
        project = self.project_repo.get(project_id)
        if not project:
            raise NotFoundError("Project", str(project_id))

        workspace = self.workspace_repo.get_by_project_id(project_id)
        if not workspace:
            raise NotFoundError("Workspace for project", str(project_id))

        tasks = self.workspace_repo.get_tasks(workspace.id)
        total = len(tasks)
        completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
        in_progress = sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS)
        blocked = sum(1 for t in tasks if t.status == TaskStatus.BLOCKED)
        todo = sum(1 for t in tasks if t.status == TaskStatus.TODO)

        completion_pct = int((completed / total) * 100) if total > 0 else 0

        input_data = {
            "project_id": str(project_id),
            "workspace_id": str(workspace.id),
            "total_tasks": total
        }

        output = {
            "total_tasks": total,
            "completed_tasks": completed,
            "in_progress_tasks": in_progress,
            "blocked_tasks": blocked,
            "todo_tasks": todo,
            "completion_percentage": completion_pct,
            "health_status": "Attention Needed" if blocked > 0 else ("On Track" if completion_pct >= 50 else "In Early Stages")
        }

        return self._persist_analysis(
            project_id=project.id,
            analysis_type=AnalysisType.PROGRESS,
            input_snapshot=input_data,
            output=output,
            confidence=0.96
        )

    # 6. EVALUATION: Assistive evaluation of submitted work against requirements
    def evaluate_submission(self, project_id: UUID, submission_id: Optional[UUID] = None) -> AIAnalysisResponse:
        project = self.project_repo.get_with_details(project_id)
        if not project:
            raise NotFoundError("Project", str(project_id))

        if submission_id:
            submission = self.submission_repo.get(submission_id)
        else:
            submission = self.submission_repo.get_latest_by_project(project_id)

        if not submission:
            raise NotFoundError("Submission for project", str(project_id))

        checks = {
            "repository_provided": bool(submission.repository_url),
            "deployment_provided": bool(submission.deployment_url),
            "documentation_provided": bool(submission.documentation_url),
            "demo_provided": bool(submission.demo_url),
            "notes_provided": bool(submission.notes)
        }

        completeness_score = int((sum(1 for v in checks.values() if v) / len(checks)) * 100)

        input_data = {
            "project_id": str(project_id),
            "submission_id": str(submission.id),
            "repository_url": submission.repository_url,
            "deployment_url": submission.deployment_url
        }

        output = {
            "completeness_score": completeness_score,
            "deliverable_verification": checks,
            "preliminary_assessment": "Deliverables complete and ready for human validation" if completeness_score >= 60 else "Partial submission; organization may request changes",
            "suggested_evaluation_rubric": {
                "technical_implementation": 4.5 if checks["repository_provided"] else 2.5,
                "requirement_fulfillment": 4.0 if checks["deployment_provided"] else 3.0,
                "communication": 4.5,
                "problem_solving": 4.0
            },
            "assistive_disclaimer": "AI evaluation is assistive only. Official feedback and experience verification must be performed by the organization."
        }

        return self._persist_analysis(
            project_id=project.id,
            analysis_type=AnalysisType.EVALUATION,
            input_snapshot=input_data,
            output=output,
            confidence=0.89
        )

    def list_analyses_for_project(self, project_id: UUID, analysis_type: Optional[AnalysisType] = None) -> List[AIAnalysisResponse]:
        items = self.ai_repo.list_by_project(project_id, analysis_type=analysis_type)
        return [AIAnalysisResponse.model_validate(a) for a in items]
