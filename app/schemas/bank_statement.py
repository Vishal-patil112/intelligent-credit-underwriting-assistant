from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import Field, model_validator

from app.schemas.common import CurrencyCode, Period, StrictBaseModel
from app.schemas.document import DocumentType
from app.schemas.extraction import BaseDocumentExtraction, ExtractedField


class BankTransaction(StrictBaseModel):
    transaction_date: date
    description: str = Field(min_length=1, max_length=1000)
    debit: Decimal | None = Field(default=None, ge=0)
    credit: Decimal | None = Field(default=None, ge=0)
    balance: Decimal | None = None
    page: int | None = Field(default=None, ge=1)
    source_text: str | None = Field(default=None, max_length=2000)

    @model_validator(mode='after')
    def validate_amount_direction(self):
        if self.debit is None and self.credit is None:
            raise ValueError('A transaction must contain a debit or a credit amount')
        return self


class MonthlyBankSummary(StrictBaseModel):
    month: str = Field(pattern=r'^\d{4}-\d{2}$')
    total_inflow: Decimal = Field(ge=0)
    total_outflow: Decimal = Field(ge=0)
    average_balance: Decimal | None = None
    minimum_balance: Decimal | None = None
    negative_balance_days: int = Field(default=0, ge=0, le=31)
    bounced_transactions: int = Field(default=0, ge=0)


class BankStatementExtraction(BaseDocumentExtraction):
    account_holder: ExtractedField[str]
    account_number_masked: ExtractedField[str] | None = None
    bank_name: ExtractedField[str] | None = None
    currency: ExtractedField[CurrencyCode] | None = None
    statement_period: ExtractedField[Period] | None = None
    opening_balance: ExtractedField[Decimal] | None = None
    closing_balance: ExtractedField[Decimal] | None = None
    transactions: list[BankTransaction] = Field(default_factory=list)
    monthly_summaries: list[MonthlyBankSummary] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_document_type(self):
        if self.document_type != DocumentType.BANK_STATEMENT:
            raise ValueError('document_type must be BANK_STATEMENT')
        return self
