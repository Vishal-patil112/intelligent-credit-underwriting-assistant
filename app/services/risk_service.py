from __future__ import annotations

from decimal import Decimal

import yaml

from app.config import get_settings
from app.schemas.common import Severity
from app.schemas.metrics import FinancialMetrics
from app.schemas.profile import CanonicalBorrowerProfile
from app.schemas.risk import RiskAssessment, RiskFactorContribution, RiskGrade, RiskLevel

settings = get_settings()


def _band_score(value, bands, default=40):
    if value is None:
        return default
    for predicate, score in bands:
        if predicate(value):
            return score
    return default


def calculate_risk(profile: CanonicalBorrowerProfile, metrics: FinancialMetrics, anomalies) -> RiskAssessment:
    cfg = yaml.safe_load(settings.risk_scorecard_path.read_text(encoding='utf-8'))
    weights = cfg['weights']
    dscr = metrics.dscr
    credit_score = profile.credit.bureau_score
    leverage = metrics.debt_to_ebitda
    liquidity = metrics.current_ratio
    margin = metrics.net_profit_margin
    net_cash = metrics.average_monthly_net_cash_flow
    bounces = profile.banking.bounced_transactions or 0
    vintage = profile.business.business_vintage_years

    category_scores = {
        'repayment_capacity': _band_score(dscr, [
            (lambda x: x >= Decimal('1.5'), 100), (lambda x: x >= Decimal('1.2'), 82),
            (lambda x: x >= Decimal('1.0'), 55), (lambda x: x < Decimal('1.0'), 25),
        ]),
        'credit_behaviour': _band_score(credit_score, [
            (lambda x: x >= 750, 100), (lambda x: x >= 700, 85), (lambda x: x >= 650, 65), (lambda x: x < 650, 30),
        ]),
        'leverage': _band_score(leverage, [
            (lambda x: x <= Decimal('2'), 100), (lambda x: x <= Decimal('3'), 85),
            (lambda x: x <= Decimal('4'), 60), (lambda x: x > Decimal('4'), 25),
        ]),
        'liquidity': _band_score(liquidity, [
            (lambda x: x >= Decimal('1.5'), 100), (lambda x: x >= Decimal('1.2'), 80),
            (lambda x: x >= Decimal('1.0'), 60), (lambda x: x < Decimal('1.0'), 30),
        ]),
        'profitability': _band_score(margin, [
            (lambda x: x >= Decimal('0.15'), 100), (lambda x: x >= Decimal('0.10'), 85),
            (lambda x: x >= Decimal('0.05'), 65), (lambda x: x >= 0, 45), (lambda x: x < 0, 20),
        ]),
        'banking_behaviour': 95 if net_cash is not None and net_cash > 0 and bounces == 0 else 75 if net_cash is not None and net_cash > 0 and bounces <= 2 else 40,
        'business_stability': _band_score(vintage, [
            (lambda x: x >= 5, 100), (lambda x: x >= 3, 80), (lambda x: x >= 2, 60), (lambda x: x < 2, 30),
        ]),
        'data_quality_anomalies': max(0, 100 - sum({Severity.LOW: 5, Severity.MEDIUM: 15, Severity.HIGH: 30, Severity.CRITICAL: 60}[a.severity] for a in anomalies)),
    }

    if (profile.credit.serious_defaults or 0) > 0:
        category_scores['credit_behaviour'] = min(category_scores['credit_behaviour'], 20)

    contributions = []
    total = Decimal('0')
    positives, negatives = [], []
    for category, weight in weights.items():
        score = Decimal(str(category_scores.get(category, 50)))
        max_points = Decimal(str(weight))
        points = (score / Decimal('100')) * max_points
        total += points
        reason = f'{category.replace("_", " ").title()} sub-score {score}/100 with weight {weight}%.'
        contributions.append(RiskFactorContribution(factor=category, category=category, points_awarded=points.quantize(Decimal('0.01')), max_points=max_points, reason=reason))
        (positives if score >= 80 else negatives if score < 60 else positives).append(reason)

    total = total.quantize(Decimal('0.01'))
    if total >= 85: grade, level = RiskGrade.A, RiskLevel.LOW
    elif total >= 70: grade, level = RiskGrade.B, RiskLevel.MODERATE
    elif total >= 55: grade, level = RiskGrade.C, RiskLevel.HIGH
    elif total >= 40: grade, level = RiskGrade.D, RiskLevel.HIGH
    else: grade, level = RiskGrade.E, RiskLevel.VERY_HIGH
    return RiskAssessment(application_id=profile.application_id, score=total, risk_grade=grade, risk_level=level,
        positive_factors=positives[:5], negative_factors=negatives[:5], contributions=contributions, scorecard_version=str(cfg.get('version', '1.0')))
