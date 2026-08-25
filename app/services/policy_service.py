from __future__ import annotations

from app.config import get_settings
from app.schemas.common import Severity
from app.schemas.document import DocumentType
from app.schemas.metrics import FinancialMetrics
from app.schemas.profile import CanonicalBorrowerProfile
from app.schemas.risk import PolicyEvaluation, PolicyRuleResult, PolicyRuleResultType
import yaml

settings = get_settings()


def apply_policy(profile: CanonicalBorrowerProfile, metrics: FinancialMetrics, present_document_types: set[DocumentType]) -> PolicyEvaluation:
    cfg = yaml.safe_load(settings.credit_policy_path.read_text(encoding='utf-8'))
    rules_cfg = cfg['rules']
    results: list[PolicyRuleResult] = []

    required = {DocumentType(x) for x in cfg.get('required_documents', [])}
    missing = sorted(x.value for x in required - present_document_types)
    results.append(PolicyRuleResult(rule_id='REQUIRED_DOCUMENTS', description='Required documents must be present',
        observed_value=sorted(x.value for x in present_document_types), threshold=sorted(x.value for x in required),
        result=PolicyRuleResultType.INCOMPLETE if missing else PolicyRuleResultType.PASS,
        severity=Severity.HIGH if missing else Severity.LOW, reason=f'Missing: {missing}' if missing else 'All required documents present'))

    def add(rule_id, desc, observed, threshold, passed, severity=Severity.HIGH, incomplete_if_none=True):
        if observed is None and incomplete_if_none:
            outcome = PolicyRuleResultType.INCOMPLETE
        else:
            outcome = PolicyRuleResultType.PASS if passed else PolicyRuleResultType.FAIL
        results.append(PolicyRuleResult(rule_id=rule_id, description=desc, observed_value=observed, threshold=threshold,
            result=outcome, severity=severity, reason=None))

    vintage = profile.business.business_vintage_years
    add('MIN_BUSINESS_VINTAGE', 'Minimum business vintage', vintage, rules_cfg['minimum_business_vintage_years'],
        vintage is not None and vintage >= rules_cfg['minimum_business_vintage_years'])
    score = profile.credit.bureau_score
    add('MIN_CREDIT_SCORE', 'Minimum bureau score', score, rules_cfg['minimum_credit_score'],
        score is not None and score >= rules_cfg['minimum_credit_score'])
    add('MIN_DSCR', 'Minimum DSCR', metrics.dscr, rules_cfg['minimum_dscr'],
        metrics.dscr is not None and metrics.dscr >= rules_cfg['minimum_dscr'])
    add('MAX_DEBT_TO_EBITDA', 'Maximum Debt/EBITDA', metrics.debt_to_ebitda, rules_cfg['maximum_debt_to_ebitda'],
        metrics.debt_to_ebitda is not None and metrics.debt_to_ebitda <= rules_cfg['maximum_debt_to_ebitda'])
    if profile.loan_request.requested_amount and profile.collateral.estimated_value:
        add('MAX_LTV', 'Maximum LTV', metrics.loan_to_value, rules_cfg['maximum_ltv'],
            metrics.loan_to_value is not None and metrics.loan_to_value <= rules_cfg['maximum_ltv'])
    defaults = profile.credit.serious_defaults
    add('MAX_SERIOUS_DELINQUENCIES', 'Maximum recent serious delinquencies/defaults', defaults,
        rules_cfg['maximum_recent_serious_delinquencies'], defaults is not None and defaults <= rules_cfg['maximum_recent_serious_delinquencies'])

    outcomes = [r.result for r in results]
    if PolicyRuleResultType.INCOMPLETE in outcomes:
        overall = PolicyRuleResultType.INCOMPLETE
    elif PolicyRuleResultType.FAIL in outcomes:
        overall = PolicyRuleResultType.FAIL
    elif PolicyRuleResultType.MANUAL_REVIEW in outcomes:
        overall = PolicyRuleResultType.MANUAL_REVIEW
    elif PolicyRuleResultType.CONDITIONAL_PASS in outcomes:
        overall = PolicyRuleResultType.CONDITIONAL_PASS
    else:
        overall = PolicyRuleResultType.PASS
    return PolicyEvaluation(application_id=profile.application_id, overall_result=overall, rules=results, policy_version=str(cfg.get('version', '1.0')))
