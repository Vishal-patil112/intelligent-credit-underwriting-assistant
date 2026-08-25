from __future__ import annotations

from decimal import Decimal
from enum import Enum

from pydantic import Field, model_validator

from app.schemas.common import StrictBaseModel
from app.schemas.document import DocumentType
from app.schemas.extraction import BaseDocumentExtraction, ExtractedField


class CreditAccountStatus(str, Enum):
    CURRENT = 'CURRENT'
    DELINQUENT = 'DELINQUENT'
    CLOSED = 'CLOSED'
    SETTLED = 'SETTLED'
    WRITTEN_OFF = 'WRITTEN_OFF'
    UNKNOWN = 'UNKNOWN'


class CreditFacility(StrictBaseModel):
    lender: str
    facility_type: str | None = None
    outstanding_balance: Decimal | None = Field(default=None, ge=0)
    monthly_obligation: Decimal | None = Field(default=None, ge=0)
    status: CreditAccountStatus = CreditAccountStatus.UNKNOWN
    days_past_due: int | None = Field(default=None, ge=0)


class CreditReportExtraction(BaseDocumentExtraction):
    bureau_score: ExtractedField[int] | None = None
    active_facilities: ExtractedField[int] | None = None
    total_outstanding_debt: ExtractedField[Decimal] | None = None
    total_monthly_obligation: ExtractedField[Decimal] | None = None
    delinquencies_12m: ExtractedField[int] | None = None
    serious_defaults: ExtractedField[int] | None = None
    hard_enquiries_6m: ExtractedField[int] | None = None
    utilization_percentage: ExtractedField[Decimal] | None = None
    facilities: list[CreditFacility] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_document_type(self):
        if self.document_type != DocumentType.CREDIT_REPORT:
            raise ValueError('document_type must be CREDIT_REPORT')
        return self
