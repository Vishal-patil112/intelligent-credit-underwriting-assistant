from decimal import Decimal

from app.schemas.profile import (
    BankingProfile,
    BusinessProfile,
    CanonicalBorrowerProfile,
    CreditProfile,
    DebtProfile,
    FinancialProfileData,
    LoanRequestProfile,
)


def test_canonical_profile_represents_underwriting_state() -> None:
    profile = CanonicalBorrowerProfile(
        application_id='APP001',
        business=BusinessProfile(
            business_name='ABC Manufacturing Pvt Ltd',
            industry='Manufacturing',
            business_vintage_years=Decimal('7'),
        ),
        loan_request=LoanRequestProfile(
            requested_amount=Decimal('5000000'),
            tenure_months=60,
            purpose='Machinery purchase',
            proposed_interest_rate=Decimal('11.5'),
        ),
        financials=FinancialProfileData(
            annual_revenue=Decimal('35000000'),
            ebitda=Decimal('6500000'),
            net_profit=Decimal('3900000'),
        ),
        existing_debt=DebtProfile(
            total_outstanding=Decimal('7500000'),
            monthly_obligation=Decimal('210000'),
        ),
        banking=BankingProfile(
            average_monthly_inflow=Decimal('2900000'),
            average_monthly_outflow=Decimal('2450000'),
            bounced_transactions=1,
        ),
        credit=CreditProfile(bureau_score=742, delinquencies_12m=0),
    )
    assert profile.credit.bureau_score == 742
    assert profile.financials.annual_revenue == Decimal('35000000')
