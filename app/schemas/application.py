from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import Field

from app.schemas.common import CurrencyCode, NonNegativeMoney, PositiveMoney, StrictBaseModel


class ApplicationStatus(str, Enum):
    DRAFT = 'DRAFT'
    DOCUMENTS_PENDING = 'DOCUMENTS_PENDING'
    READY_FOR_ANALYSIS = 'READY_FOR_ANALYSIS'
    ANALYZING = 'ANALYZING'
    HUMAN_REVIEW = 'HUMAN_REVIEW'
    DECIDED = 'DECIDED'
    FAILED = 'FAILED'


class BusinessType(str, Enum):
    SOLE_PROPRIETORSHIP = 'SOLE_PROPRIETORSHIP'
    PARTNERSHIP = 'PARTNERSHIP'
    LLP = 'LLP'
    PRIVATE_LIMITED = 'PRIVATE_LIMITED'
    PUBLIC_LIMITED = 'PUBLIC_LIMITED'
    OTHER = 'OTHER'


class OwnerInput(StrictBaseModel):
    name: str = Field(min_length=2, max_length=200)
    ownership_percentage: Decimal = Field(ge=0, le=100)
    role: str | None = Field(default=None, max_length=100)


class LoanRequestInput(StrictBaseModel):
    requested_amount: PositiveMoney
    currency: CurrencyCode = CurrencyCode.INR
    tenure_months: int = Field(ge=1, le=360)
    purpose: str = Field(min_length=3, max_length=500)
    proposed_interest_rate: Decimal | None = Field(default=None, ge=0, le=100)
    collateral_offered: bool = False


class ApplicationCreate(StrictBaseModel):
    customer_id: str | None = Field(default=None, max_length=100)
    business_name: str = Field(min_length=2, max_length=255)
    business_type: BusinessType | None = None
    industry: str | None = Field(default=None, max_length=150)
    business_vintage_years: Decimal | None = Field(default=None, ge=0, le=200)
    registration_number: str | None = Field(default=None, max_length=100)
    tax_identifier: str | None = Field(default=None, max_length=100)
    owners: list[OwnerInput] = Field(default_factory=list)
    declared_annual_revenue: NonNegativeMoney | None = None
    declared_existing_obligations: NonNegativeMoney | None = None
    loan_request: LoanRequestInput
    consent_confirmed: bool = False


class ApplicationRecord(ApplicationCreate):
    application_id: str
    status: ApplicationStatus = ApplicationStatus.DOCUMENTS_PENDING
    created_at: datetime
    updated_at: datetime
