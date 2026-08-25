from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import Field, model_validator

from app.schemas.common import StrictBaseModel


class RecommendationStatus(str, Enum):
    APPROVE = 'APPROVE'
    CONDITIONAL_APPROVE = 'CONDITIONAL_APPROVE'
    MANUAL_REVIEW = 'MANUAL_REVIEW'
    REJECT = 'REJECT'
    REQUEST_MORE_DOCUMENTS = 'REQUEST_MORE_DOCUMENTS'


class UnderwritingRecommendation(StrictBaseModel):
    application_id: str
    status: RecommendationStatus
    recommended_amount: Decimal | None = Field(default=None, ge=0)
    conditions: list[str] = Field(default_factory=list)
    positive_factors: list[str] = Field(default_factory=list)
    risk_factors: list[str] = Field(default_factory=list)
    explanation: str
    evidence_ids: list[str] = Field(default_factory=list)
    requires_human_review: bool = True
    generated_at: datetime
    model_version: str | None = None
    policy_version: str | None = None

    @model_validator(mode='after')
    def require_conditions_for_conditional_approval(self):
        if self.status == RecommendationStatus.CONDITIONAL_APPROVE and not self.conditions:
            raise ValueError('CONDITIONAL_APPROVE requires at least one condition')
        return self
