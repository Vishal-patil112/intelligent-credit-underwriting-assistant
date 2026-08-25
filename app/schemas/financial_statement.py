from __future__ import annotations

from decimal import Decimal

from pydantic import model_validator

from app.schemas.common import CurrencyCode, Period
from app.schemas.document import DocumentType
from app.schemas.extraction import BaseDocumentExtraction, ExtractedField


class FinancialStatementExtraction(BaseDocumentExtraction):
    business_name: ExtractedField[str] | None = None
    reporting_period: ExtractedField[Period] | None = None
    currency: ExtractedField[CurrencyCode] | None = None

    revenue: ExtractedField[Decimal] | None = None
    cost_of_goods_sold: ExtractedField[Decimal] | None = None
    gross_profit: ExtractedField[Decimal] | None = None
    operating_expenses: ExtractedField[Decimal] | None = None
    ebitda: ExtractedField[Decimal] | None = None
    net_profit: ExtractedField[Decimal] | None = None

    cash_and_equivalents: ExtractedField[Decimal] | None = None
    current_assets: ExtractedField[Decimal] | None = None
    current_liabilities: ExtractedField[Decimal] | None = None
    total_assets: ExtractedField[Decimal] | None = None
    total_liabilities: ExtractedField[Decimal] | None = None
    total_debt: ExtractedField[Decimal] | None = None
    receivables: ExtractedField[Decimal] | None = None
    inventory: ExtractedField[Decimal] | None = None
    equity: ExtractedField[Decimal] | None = None

    @model_validator(mode='after')
    def validate_document_type(self):
        if self.document_type not in {
            DocumentType.FINANCIAL_STATEMENT,
            DocumentType.INCOME_STATEMENT,
            DocumentType.BALANCE_SHEET,
        }:
            raise ValueError('financial extraction requires a financial statement document type')
        return self
