from __future__ import annotations

from decimal import Decimal

from pydantic import Field

from app.schemas.common import CurrencyCode, DataQualityStatus, StrictBaseModel


class BusinessProfile(StrictBaseModel):
    business_name: str
    industry: str | None = None
    business_type: str | None = None
    business_vintage_years: Decimal | None = Field(default=None, ge=0)
    registration_number: str | None = None
    tax_identifier: str | None = None


class LoanRequestProfile(StrictBaseModel):
    requested_amount: Decimal = Field(gt=0)
    currency: CurrencyCode = CurrencyCode.INR
    tenure_months: int = Field(ge=1, le=360)
    purpose: str
    proposed_interest_rate: Decimal | None = Field(default=None, ge=0, le=100)


class FinancialProfileData(StrictBaseModel):
    annual_revenue: Decimal | None = None
    previous_annual_revenue: Decimal | None = None
    ebitda: Decimal | None = None
    net_profit: Decimal | None = None
    cash_balance: Decimal | None = None
    current_assets: Decimal | None = None
    current_liabilities: Decimal | None = None
    total_assets: Decimal | None = None
    total_liabilities: Decimal | None = None
    receivables: Decimal | None = None
    inventory: Decimal | None = None
    equity: Decimal | None = None


class DebtProfile(StrictBaseModel):
    total_outstanding: Decimal | None = Field(default=None, ge=0)
    monthly_obligation: Decimal | None = Field(default=None, ge=0)
    disclosed_facilities: int | None = Field(default=None, ge=0)
    observed_lender_payments: int | None = Field(default=None, ge=0)


class BankingProfile(StrictBaseModel):
    average_monthly_balance: Decimal | None = None
    minimum_balance: Decimal | None = None
    average_monthly_inflow: Decimal | None = Field(default=None, ge=0)
    average_monthly_outflow: Decimal | None = Field(default=None, ge=0)
    negative_balance_days: int | None = Field(default=None, ge=0)
    bounced_transactions: int | None = Field(default=None, ge=0)
    cash_flow_volatility: Decimal | None = Field(default=None, ge=0)


class CreditProfile(StrictBaseModel):
    bureau_score: int | None = Field(default=None, ge=0, le=1000)
    active_facilities: int | None = Field(default=None, ge=0)
    total_outstanding: Decimal | None = Field(default=None, ge=0)
    monthly_obligation: Decimal | None = Field(default=None, ge=0)
    delinquencies_12m: int | None = Field(default=None, ge=0)
    serious_defaults: int | None = Field(default=None, ge=0)
    hard_enquiries_6m: int | None = Field(default=None, ge=0)
    utilization_percentage: Decimal | None = Field(default=None, ge=0, le=100)


class CollateralProfile(StrictBaseModel):
    collateral_type: str | None = None
    owner_name: str | None = None
    estimated_value: Decimal | None = Field(default=None, ge=0)
    encumbrance: bool | None = None
    valuation_date: str | None = None


class DataQualityIssue(StrictBaseModel):
    field_name: str
    status: DataQualityStatus
    message: str
    document_ids: list[str] = Field(default_factory=list)


class CanonicalBorrowerProfile(StrictBaseModel):
    application_id: str
    business: BusinessProfile
    loan_request: LoanRequestProfile
    financials: FinancialProfileData = Field(default_factory=FinancialProfileData)
    existing_debt: DebtProfile = Field(default_factory=DebtProfile)
    banking: BankingProfile = Field(default_factory=BankingProfile)
    credit: CreditProfile = Field(default_factory=CreditProfile)
    collateral: CollateralProfile = Field(default_factory=CollateralProfile)
    data_quality_issues: list[DataQualityIssue] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
