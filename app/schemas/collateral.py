from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import model_validator

from app.schemas.document import DocumentType
from app.schemas.extraction import BaseDocumentExtraction, ExtractedField


class CollateralExtraction(BaseDocumentExtraction):
    collateral_type: ExtractedField[str] | None = None
    asset_description: ExtractedField[str] | None = None
    owner_name: ExtractedField[str] | None = None
    estimated_value: ExtractedField[Decimal] | None = None
    encumbrance: ExtractedField[bool] | None = None
    valuation_date: ExtractedField[date] | None = None

    @model_validator(mode='after')
    def validate_document_type(self):
        if self.document_type != DocumentType.COLLATERAL_DOCUMENT:
            raise ValueError('document_type must be COLLATERAL_DOCUMENT')
        return self
