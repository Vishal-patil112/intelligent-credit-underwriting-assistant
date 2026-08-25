from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import model_validator

from app.schemas.common import Period
from app.schemas.document import DocumentType
from app.schemas.extraction import BaseDocumentExtraction, ExtractedField


class TaxReturnExtraction(BaseDocumentExtraction):
    business_name: ExtractedField[str] | None = None
    tax_identifier: ExtractedField[str] | None = None
    filing_period: ExtractedField[Period] | None = None
    reported_turnover: ExtractedField[Decimal] | None = None
    taxable_income: ExtractedField[Decimal] | None = None
    tax_paid: ExtractedField[Decimal] | None = None
    filing_date: ExtractedField[date] | None = None

    @model_validator(mode='after')
    def validate_document_type(self):
        if self.document_type != DocumentType.TAX_RETURN:
            raise ValueError('document_type must be TAX_RETURN')
        return self
