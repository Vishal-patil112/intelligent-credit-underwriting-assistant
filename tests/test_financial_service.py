from decimal import Decimal
from app.schemas.profile import BusinessProfile, CanonicalBorrowerProfile, CollateralProfile, CreditProfile, DebtProfile, FinancialProfileData, LoanRequestProfile, BankingProfile
from app.services.financial_service import calculate_emi, calculate_metrics


def sample_profile():
    return CanonicalBorrowerProfile(application_id='APP1', business=BusinessProfile(business_name='ABC', business_vintage_years=7),
        loan_request=LoanRequestProfile(requested_amount=Decimal('5000000'), tenure_months=60, purpose='Machinery', proposed_interest_rate=Decimal('11.5')),
        financials=FinancialProfileData(annual_revenue=Decimal('35000000'), previous_annual_revenue=Decimal('32000000'), ebitda=Decimal('8000000'), net_profit=Decimal('4200000'), current_assets=Decimal('12000000'), current_liabilities=Decimal('6000000')),
        existing_debt=DebtProfile(total_outstanding=Decimal('4000000'), monthly_obligation=Decimal('120000')),
        banking=BankingProfile(average_monthly_inflow=Decimal('2900000'), average_monthly_outflow=Decimal('2450000')),
        credit=CreditProfile(bureau_score=760), collateral=CollateralProfile(estimated_value=Decimal('8000000')))


def test_emi_and_metrics_are_deterministic():
    emi = calculate_emi(Decimal('5000000'), Decimal('11.5'), 60)
    assert emi > 100000
    metrics = calculate_metrics(sample_profile())
    assert metrics.dscr > Decimal('1.2')
    assert metrics.current_ratio == Decimal('2.0000')
    assert metrics.loan_to_value == Decimal('0.6250')
