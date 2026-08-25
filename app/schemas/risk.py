from __future__ import annotations

from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import Field

from app.schemas.common import Confidence, Severity, StrictBaseModel


class RiskLevel(str, Enum):
    LOW = 'LOW'
    MODERATE = 'MODERATE'
    HIGH = 'HIGH'
    VERY_HIGH = 'VERY_HIGH'


class RiskGrade(str, Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    E = 'E'


class PolicyRuleResultType(str, Enum):
    PASS = 'PASS'
    CONDITIONAL_PASS = 'CONDITIONAL_PASS'
    MANUAL_REVIEW = 'MANUAL_REVIEW'
    FAIL = 'FAIL'
    INCOMPLETE = 'INCOMPLETE'


class Anomaly(StrictBaseModel):
    anomaly_id: str
    anomaly_type: str
    severity: Severity
    description: str
    confidence: Confidence = 1.0
    evidence_ids: list[str] = Field(default_factory=list)
    requires_review: bool = True


class RiskFactorContribution(StrictBaseModel):
    factor: str
    category: str
    points_awarded: Decimal
    max_points: Decimal = Field(gt=0)
    reason: str


class RiskAssessment(StrictBaseModel):
    application_id: str
    score: Decimal = Field(ge=0, le=100)
    risk_grade: RiskGrade
    risk_level: RiskLevel
    positive_factors: list[str] = Field(default_factory=list)
    negative_factors: list[str] = Field(default_factory=list)
    contributions: list[RiskFactorContribution] = Field(default_factory=list)
    scorecard_version: str


class PolicyRuleResult(StrictBaseModel):
    rule_id: str
    description: str
    observed_value: Any | None = None
    threshold: Any | None = None
    result: PolicyRuleResultType
    severity: Severity
    reason: str | None = None


class PolicyEvaluation(StrictBaseModel):
    application_id: str
    overall_result: PolicyRuleResultType
    rules: list[PolicyRuleResult] = Field(default_factory=list)
    policy_version: str
