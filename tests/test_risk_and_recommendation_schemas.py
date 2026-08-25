from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.recommendation import RecommendationStatus, UnderwritingRecommendation
from app.schemas.review import UnderwriterAction, UnderwriterDecisionRequest
from app.schemas.risk import RiskAssessment, RiskGrade, RiskLevel


def test_risk_assessment_schema() -> None:
    result = RiskAssessment(
        application_id='APP001',
        score=Decimal('78'),
        risk_grade=RiskGrade.B,
        risk_level=RiskLevel.MODERATE,
        positive_factors=['Strong DSCR'],
        negative_factors=['Moderate leverage'],
        scorecard_version='1.0-hackathon',
    )
    assert result.score == Decimal('78')


def test_conditional_approval_requires_condition() -> None:
    with pytest.raises(ValidationError):
        UnderwritingRecommendation(
            application_id='APP001',
            status=RecommendationStatus.CONDITIONAL_APPROVE,
            recommended_amount=Decimal('4000000'),
            explanation='Conditional recommendation.',
            generated_at=datetime.now(timezone.utc),
        )


def test_override_requires_reason() -> None:
    with pytest.raises(ValidationError):
        UnderwriterDecisionRequest(action=UnderwriterAction.OVERRIDE_AI_RECOMMENDATION)
