from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from statistics import pstdev

from app.schemas.metrics import FinancialMetrics
from app.schemas.profile import CanonicalBorrowerProfile

Q = Decimal('0.0001')


def _ratio(a, b):
    if a is None or b in (None, 0, Decimal('0')):
        return None
    return (Decimal(a) / Decimal(b)).quantize(Q, rounding=ROUND_HALF_UP)


def calculate_emi(principal: Decimal, annual_rate_percent: Decimal, tenure_months: int) -> Decimal:
    p = Decimal(principal)
    if tenure_months <= 0:
        raise ValueError('tenure_months must be positive')
    monthly_rate = Decimal(annual_rate_percent) / Decimal('1200')
    if monthly_rate == 0:
        return (p / tenure_months).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    factor = (Decimal('1') + monthly_rate) ** tenure_months
    emi = p * monthly_rate * factor / (factor - Decimal('1'))
    return emi.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculate_metrics(profile: CanonicalBorrowerProfile, *, override_amount: Decimal | None = None,
                      override_rate: Decimal | None = None, override_tenure: int | None = None) -> FinancialMetrics:
    amount = override_amount or profile.loan_request.requested_amount
    rate = override_rate if override_rate is not None else (profile.loan_request.proposed_interest_rate or Decimal('12'))
    tenure = override_tenure or profile.loan_request.tenure_months
    proposed_emi = calculate_emi(amount, rate, tenure)
    existing_monthly = profile.existing_debt.monthly_obligation or Decimal('0')
    annual_debt_service = (existing_monthly + proposed_emi) * Decimal('12')
    ebitda = profile.financials.ebitda
    revenue = profile.financials.annual_revenue
    net_profit = profile.financials.net_profit
    total_debt = profile.existing_debt.total_outstanding
    inflow = profile.banking.average_monthly_inflow
    outflow = profile.banking.average_monthly_outflow
    monthly_net = (inflow - outflow) if inflow is not None and outflow is not None else None
    annual_operating_cash = monthly_net * 12 if monthly_net is not None else None
    cash_available = ebitda if ebitda is not None else (annual_operating_cash if annual_operating_cash is not None else net_profit)

    return FinancialMetrics(
        application_id=profile.application_id,
        dscr=_ratio(cash_available, annual_debt_service),
        debt_to_ebitda=_ratio(total_debt, ebitda),
        current_ratio=_ratio(profile.financials.current_assets, profile.financials.current_liabilities),
        net_profit_margin=_ratio(net_profit, revenue),
        revenue_growth=_ratio((revenue - profile.financials.previous_annual_revenue) if revenue is not None and profile.financials.previous_annual_revenue is not None else None, profile.financials.previous_annual_revenue),
        average_monthly_net_cash_flow=monthly_net,
        debt_burden_ratio=_ratio(existing_monthly + proposed_emi, inflow),
        loan_to_value=_ratio(amount, profile.collateral.estimated_value),
        cash_flow_volatility=profile.banking.cash_flow_volatility,
        annual_scheduled_debt_service=annual_debt_service.quantize(Decimal('0.01')),
        formula_version='1.0-hackathon-ebitda-proxy',
        input_evidence_ids=profile.evidence_ids,
    )
