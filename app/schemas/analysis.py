from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from app.schemas.common import Confidence, StrictBaseModel
from app.schemas.document import DocumentType
from app.schemas.metrics import FinancialMetrics
from app.schemas.profile import CanonicalBorrowerProfile
from app.schemas.recommendation import UnderwritingRecommendation
from app.schemas.risk import Anomaly, PolicyEvaluation, RiskAssessment


class GenericExtractedField(StrictBaseModel):
    value: Any | None = None
    confidence: Confidence = 0.8
    page: int | None = Field(default=1, ge=1)
    source_text: str | None = Field(default=None, max_length=3000)


class GenericDocumentExtraction(StrictBaseModel):
    document_id: str
    document_type: DocumentType
    fields: dict[str, GenericExtractedField] = Field(default_factory=dict)
    extraction_confidence: Confidence = 0.8
    extractor: str = 'heuristic'
    model_version: str | None = None
    warnings: list[str] = Field(default_factory=list)


class AnalysisBundle(StrictBaseModel):
    application_id: str
    profile: CanonicalBorrowerProfile
    metrics: FinancialMetrics
    anomalies: list[Anomaly]
    risk: RiskAssessment
    policy: PolicyEvaluation
    recommendation: UnderwritingRecommendation
    completed_at: datetime
