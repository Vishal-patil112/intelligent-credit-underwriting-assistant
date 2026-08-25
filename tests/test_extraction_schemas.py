from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.document import DocumentType
from app.schemas.extraction import EvidenceSource, ExtractedField
from app.schemas.financial_statement import FinancialStatementExtraction


def source() -> EvidenceSource:
    return EvidenceSource(
        document_id='DOC002',
        document_type=DocumentType.FINANCIAL_STATEMENT,
        page=3,
        source_text='Revenue from Operations 35,000,000',
    )


def test_evidence_backed_financial_extraction() -> None:
    result = FinancialStatementExtraction(
        document_id='DOC002',
        document_type=DocumentType.FINANCIAL_STATEMENT,
        extraction_confidence=0.97,
        model_version='gemini-3.5-flash-lite',
        revenue=ExtractedField[Decimal](
            value=Decimal('35000000'),
            confidence=0.96,
            source=source(),
        ),
    )
    assert result.revenue is not None
    assert result.revenue.value == Decimal('35000000')
    assert result.revenue.source.page == 3


def test_confidence_range_is_enforced() -> None:
    with pytest.raises(ValidationError):
        ExtractedField[str](value='x', confidence=1.2, source=source())
