import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Index, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.types import GUID, JSONBType, EnumType
from app.models.enums import AnalysisType


def utcnow():
    return datetime.now(timezone.utc)


class AIAnalysis(Base):
    __tablename__ = "ai_analyses"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    analysis_type = Column(
        EnumType(AnalysisType, name="ai_analysis_type"),
        nullable=False,
        index=True
    )
    input_snapshot = Column(JSONBType(), nullable=False)
    output = Column(JSONBType(), nullable=False)
    model_name = Column(String(150), nullable=True)
    confidence = Column(Numeric(5, 4), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    # Relationships
    project = relationship("Project", back_populates="ai_analyses")

    __table_args__ = (
        Index("idx_ai_analyses_project_type", "project_id", "analysis_type"),
    )
