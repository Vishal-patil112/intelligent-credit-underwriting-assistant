from __future__ import annotations

from app.schemas.document import DocumentType
from app.schemas.recommendation import RecommendationStatus
from app.schemas.risk import PolicyRuleResultType
from app.schemas.simulation import LoanSimulationRequest, LoanSimulationResult
from app.services.financial_service import calculate_emi, calculate_metrics
from app.services.policy_service import apply_policy
from datetime import datetime, timezone
from uuid import uuid4


def simulate(profile, scenario: LoanSimulationRequest, present_document_types: set[DocumentType]) -> LoanSimulationResult:
    metrics = calculate_metrics(profile, override_amount=scenario.amount, override_rate=scenario.interest_rate, override_tenure=scenario.tenure_months)
    policy = apply_policy(profile, metrics, present_document_types)
    if policy.overall_result == PolicyRuleResultType.PASS:
        rec = RecommendationStatus.APPROVE
    elif policy.overall_result == PolicyRuleResultType.INCOMPLETE:
        rec = RecommendationStatus.REQUEST_MORE_DOCUMENTS
    elif policy.overall_result == PolicyRuleResultType.FAIL:
        rec = RecommendationStatus.MANUAL_REVIEW
    else:
        rec = RecommendationStatus.CONDITIONAL_APPROVE
    return LoanSimulationResult(simulation_id=f'SIM-{uuid4().hex[:10].upper()}', application_id=profile.application_id,
        scenario=scenario, emi=calculate_emi(scenario.amount, scenario.interest_rate, scenario.tenure_months),
        metrics=metrics, policy_result=policy.overall_result, recommendation=rec, created_at=datetime.now(timezone.utc))
