from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.ai import AIAnalysis
from app.models.enums import AnalysisType
from app.repositories.base import BaseRepository


class AIRepository(BaseRepository[AIAnalysis]):
    def __init__(self, db: Session):
        super().__init__(AIAnalysis, db)

    def list_by_project(
        self,
        project_id: UUID,
        analysis_type: Optional[AnalysisType] = None
    ) -> List[AIAnalysis]:
        query = self.db.query(AIAnalysis).filter(AIAnalysis.project_id == project_id)
        if analysis_type:
            query = query.filter(AIAnalysis.analysis_type == analysis_type)
        return query.order_by(AIAnalysis.created_at.desc()).all()

    def get_latest_analysis(
        self,
        project_id: UUID,
        analysis_type: AnalysisType
    ) -> Optional[AIAnalysis]:
        return (
            self.db.query(AIAnalysis)
            .filter(
                AIAnalysis.project_id == project_id,
                AIAnalysis.analysis_type == analysis_type
            )
            .order_by(AIAnalysis.created_at.desc())
            .first()
        )
