import pytest
from pydantic import ValidationError

from app.schemas.application import LoanRequestInput


def test_unexpected_fields_are_rejected() -> None:
    with pytest.raises(ValidationError):
        LoanRequestInput(
            requested_amount=100000,
            tenure_months=12,
            purpose="Working capital",
            invented_llm_field="must-not-enter-state",
        )
