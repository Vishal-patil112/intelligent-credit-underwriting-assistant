from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.application import ApplicationCreate, LoanRequestInput


def test_valid_application_schema() -> None:
    application = ApplicationCreate(
        business_name='ABC Manufacturing Pvt Ltd',
        business_vintage_years=Decimal('7'),
        declared_annual_revenue=Decimal('35000000'),
        consent_confirmed=True,
        loan_request=LoanRequestInput(
            requested_amount=Decimal('5000000'),
            tenure_months=60,
            purpose='Purchase of machinery',
            proposed_interest_rate=Decimal('11.5'),
        ),
    )
    assert application.loan_request.requested_amount == Decimal('5000000')
    assert application.loan_request.currency.value == 'INR'


def test_requested_amount_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        LoanRequestInput(
            requested_amount=Decimal('0'),
            tenure_months=60,
            purpose='Working capital',
        )
