from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import Enum

from pydantic import Field, model_validator

from app.schemas.common import StrictBaseModel
from app.schemas.document import DocumentType
from app.schemas.extraction import BaseDocumentExtraction, ExtractedField


class SecurityType(str, Enum):
    SECURED = 'SECURED'
    UNSECURED = 'UNSECURED'
    UNKNOWN = 'UNKNOWN'


class ExistingLoanFacility(StrictBaseModel):
    lender: str
    loan_type: str | None = None
    outstanding_principal: Decimal | None = Field(default=None, ge=0)
    emi: Decimal | None = Field(default=None, ge=0)
    interest_rate: Decimal | None = Field(default=None, ge=0, le=100)
    maturity_date: date | None = None
    overdue_amount: Decimal | None = Field(default=None, ge=0)
    days_past_due: int | None = Field(default=None, ge=0)
    security_type: SecurityType = SecurityType.UNKNOWN


class LoanStatementExtraction(BaseDocumentExtraction):
    lender: ExtractedField[str] | None = None
    loan_type: ExtractedField[str] | None = None
    outstanding_principal: ExtractedField[Decimal] | None = None
    emi: ExtractedField[Decimal] | None = None
    interest_rate: ExtractedField[Decimal] | None = None
    maturity_date: ExtractedField[date] | None = None
    overdue_amount: ExtractedField[Decimal] | None = None
    days_past_due: ExtractedField[int] | None = None
    security_type: ExtractedField[SecurityType] | None = None
    facilities: list[ExistingLoanFacility] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_document_type(self):
        if self.document_type != DocumentType.EXISTING_LOAN_STATEMENT:
            raise ValueError('document_type must be EXISTING_LOAN_STATEMENT')
        return self
