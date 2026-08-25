from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from decimal import Decimal

from app.llm import GeminiClient
from app.schemas.common import Severity
from app.schemas.profile import CanonicalBorrowerProfile
from app.schemas.recommendation import RecommendationStatus, UnderwritingRecommendation
from app.schemas.risk import PolicyEvaluation, PolicyRuleResultType, RiskAssessment, RiskGrade

logger = logging.getLogger(__name__)

def build_recommendation(profile: CanonicalBorrowerProfile, metrics, anomalies, risk: RiskAssessment,
                         policy: PolicyEvaluation, llm: GeminiClient | None = None) -> UnderwritingRecommendation:
    hard_anomaly = any(a.severity in {Severity.HIGH, Severity.CRITICAL} for a in anomalies)
    conditions: list[str] = []
    if policy.overall_result == PolicyRuleResultType.INCOMPLETE:
        status = RecommendationStatus.REQUEST_MORE_DOCUMENTS
        conditions = [r.reason for r in policy.rules if r.result == PolicyRuleResultType.INCOMPLETE and r.reason]
    elif policy.overall_result == PolicyRuleResultType.FAIL:
        status = RecommendationStatus.REJECT
    elif hard_anomaly or risk.risk_grade in {RiskGrade.C, RiskGrade.D, RiskGrade.E}:
        status = RecommendationStatus.MANUAL_REVIEW
    elif risk.score >= Decimal('82'):
        status = RecommendationStatus.APPROVE
    else:
        status = RecommendationStatus.CONDITIONAL_APPROVE
        conditions = ['Underwriter to verify borderline risk factors before sanction.']

    requested = profile.loan_request.requested_amount
    recommended_amount = requested if status == RecommendationStatus.APPROVE else (requested * Decimal('0.80')).quantize(Decimal('0.01')) if status == RecommendationStatus.CONDITIONAL_APPROVE else None
    summary = _deterministic_summary(profile, metrics, anomalies, risk, policy, status)

    if llm and llm.enabled:
        context = {
            'borrower': profile.model_dump(mode='json'), 'metrics': metrics.model_dump(mode='json'),
            'risk': risk.model_dump(mode='json'), 'policy': policy.model_dump(mode='json'),
            'anomalies': [a.model_dump(mode='json') for a in anomalies], 'fixed_status': status.value,
            'fixed_recommended_amount': float(recommended_amount) if recommended_amount is not None else None,
        }
        prompt = """You are an underwriting memo writer. Explain the supplied validated structured results concisely.
Do not invent or recalculate numbers. Do not change fixed_status or fixed_recommended_amount.
Cover borrower overview, repayment capacity, banking/credit, positive factors, risk factors, policy exceptions and recommendation.
Return plain text only. Structured context:\n""" + json.dumps(context, default=str)
        try:
            summary = llm.generate_text(prompt)

        except Exception as exc:
            logger.warning(
                "gemini_credit_summary_failed_falling_back "
                "application_id=%s error=%s",
                profile.application_id,
                type(exc).__name__,
            )

    return UnderwritingRecommendation(application_id=profile.application_id, status=status,
        recommended_amount=recommended_amount, conditions=conditions,
        positive_factors=risk.positive_factors, risk_factors=risk.negative_factors + [a.description for a in anomalies[:3]],
        explanation=summary, evidence_ids=profile.evidence_ids,
        requires_human_review=True, generated_at=datetime.now(timezone.utc),
        model_version=(llm.model if llm and llm.enabled else 'deterministic-summary-v1'), policy_version=policy.policy_version)


def _deterministic_summary(profile, metrics, anomalies, risk, policy, status) -> str:
    return (
        f'{profile.business.business_name} requests {profile.loan_request.requested_amount} {profile.loan_request.currency.value} '
        f'for {profile.loan_request.purpose}. Risk score is {risk.score} ({risk.risk_grade.value}); '
        f'DSCR is {metrics.dscr if metrics.dscr is not None else "unavailable"}, policy result is {policy.overall_result.value}. '
        f'{len(anomalies)} anomaly/anomalies were identified. Recommendation: {status.value}. '
        'This recommendation is an underwriting aid and remains subject to authorized human review and bank policy.'
    )
