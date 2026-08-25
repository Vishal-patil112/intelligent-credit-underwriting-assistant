"""Local Phase 2 smoke test for the core schema contracts."""

from decimal import Decimal
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.schemas.application import ApplicationCreate, LoanRequestInput
from app.schemas.document import DocumentType
from app.schemas.extraction import EvidenceSource, ExtractedField
from app.schemas.financial_statement import FinancialStatementExtraction
from app.schemas.profile import BusinessProfile, CanonicalBorrowerProfile, LoanRequestProfile


def main() -> None:
    application = ApplicationCreate(
        business_name="ABC Manufacturing Pvt Ltd",
        business_vintage_years=Decimal("7"),
        consent_confirmed=True,
        loan_request=LoanRequestInput(
            requested_amount=Decimal("5000000"),
            tenure_months=60,
            purpose="Purchase of machinery",
            proposed_interest_rate=Decimal("11.5"),
        ),
    )

    source = EvidenceSource(
        document_id="DOC002",
        document_type=DocumentType.FINANCIAL_STATEMENT,
        page=3,
        source_text="Revenue from Operations 35,000,000",
    )

    extraction = FinancialStatementExtraction(
        document_id="DOC002",
        document_type=DocumentType.FINANCIAL_STATEMENT,
        extraction_confidence=0.97,
        model_version="future-gemini-extractor",
        revenue=ExtractedField[Decimal](
            value=Decimal("35000000"),
            confidence=0.96,
            source=source,
        ),
    )

    profile = CanonicalBorrowerProfile(
        application_id="APP001",
        business=BusinessProfile(
            business_name=application.business_name,
            business_vintage_years=application.business_vintage_years,
        ),
        loan_request=LoanRequestProfile(
            requested_amount=application.loan_request.requested_amount,
            tenure_months=application.loan_request.tenure_months,
            purpose=application.loan_request.purpose,
            proposed_interest_rate=application.loan_request.proposed_interest_rate,
        ),
    )

    assert extraction.revenue is not None
    assert extraction.revenue.value == Decimal("35000000")
    assert extraction.revenue.source.page == 3
    assert profile.application_id == "APP001"
    print("PHASE_2_SCHEMA_CHECK_OK")


if __name__ == "__main__":
    main()
