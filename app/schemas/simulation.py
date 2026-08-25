from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import Field

from app.schemas.common import CurrencyCode, StrictBaseModel
from app.schemas.metrics import FinancialMetrics
from app.schemas.recommendation import RecommendationStatus
from app.schemas.risk import PolicyRuleResultType


class LoanSimulationRequest(StrictBaseModel):
    amount: Decimal = Field(gt=0)
    currency: CurrencyCode = CurrencyCode.INR
    interest_rate: Decimal = Field(ge=0, le=100)
    tenure_months: int = Field(ge=1, le=360)


class LoanSimulationResult(StrictBaseModel):
    simulation_id: str
    application_id: str
    scenario: LoanSimulationRequest
    emi: Decimal = Field(ge=0)
    metrics: FinancialMetrics
    policy_result: PolicyRuleResultType
    recommendation: RecommendationStatus
    created_at: datetime
