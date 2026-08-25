from __future__ import annotations

from decimal import Decimal

from pydantic import Field

from app.schemas.common import StrictBaseModel


class FinancialMetrics(StrictBaseModel):
    application_id: str
    dscr: Decimal | None = Field(default=None, ge=0)
    debt_to_ebitda: Decimal | None = None
    current_ratio: Decimal | None = None
    net_profit_margin: Decimal | None = None
    revenue_growth: Decimal | None = None
    average_monthly_net_cash_flow: Decimal | None = None
    debt_burden_ratio: Decimal | None = None
    loan_to_value: Decimal | None = None
    cash_flow_volatility: Decimal | None = None
    annual_scheduled_debt_service: Decimal | None = Field(default=None, ge=0)
    formula_version: str = '1.0'
    input_evidence_ids: list[str] = Field(default_factory=list)
