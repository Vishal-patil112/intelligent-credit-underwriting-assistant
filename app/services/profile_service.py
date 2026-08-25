from __future__ import annotations

from decimal import Decimal

from app.schemas.analysis import GenericDocumentExtraction
from app.schemas.application import ApplicationRecord
from app.schemas.document import DocumentType
from app.schemas.profile import (
    BankingProfile, BusinessProfile, CanonicalBorrowerProfile, CollateralProfile,
    CreditProfile, DebtProfile, FinancialProfileData, LoanRequestProfile,
)


def _value(extraction: GenericDocumentExtraction | None, field: str):
    if not extraction:
        return None
    item = extraction.fields.get(field)
    return item.value if item else None


def _dec(value):
    return Decimal(str(value)) if value is not None else None


def build_profile(application: ApplicationRecord, extractions: list[GenericDocumentExtraction]) -> CanonicalBorrowerProfile:
    by_type = {item.document_type: item for item in extractions}
    financial = by_type.get(DocumentType.FINANCIAL_STATEMENT) or by_type.get(DocumentType.INCOME_STATEMENT) or by_type.get(DocumentType.BALANCE_SHEET)
    tax = by_type.get(DocumentType.TAX_RETURN)
    bank = by_type.get(DocumentType.BANK_STATEMENT)
    credit = by_type.get(DocumentType.CREDIT_REPORT)
    loan = by_type.get(DocumentType.EXISTING_LOAN_STATEMENT)
    collateral = by_type.get(DocumentType.COLLATERAL_DOCUMENT)

    revenue = _value(financial, 'revenue') or _value(tax, 'reported_turnover') or application.declared_annual_revenue
    total_debt_candidates = [v for v in (
        _value(financial, 'total_debt'), _value(credit, 'total_outstanding_debt'),
        _value(loan, 'total_outstanding'), _value(loan, 'outstanding_principal'),
        application.declared_existing_obligations,
    ) if v is not None]
    total_debt = max((_dec(v) for v in total_debt_candidates), default=None)
    obligation_candidates = [v for v in (_value(credit, 'total_monthly_obligation'), _value(loan, 'total_monthly_obligation'), _value(loan, 'emi')) if v is not None]
    monthly_obligation = max((_dec(v) for v in obligation_candidates), default=Decimal('0')) if obligation_candidates else None

    return CanonicalBorrowerProfile(
        application_id=application.application_id,
        business=BusinessProfile(
            business_name=application.business_name,
            industry=application.industry,
            business_type=application.business_type.value if application.business_type else None,
            business_vintage_years=application.business_vintage_years,
            registration_number=application.registration_number,
            tax_identifier=application.tax_identifier or _value(tax, 'tax_identifier'),
        ),
        loan_request=LoanRequestProfile(
            requested_amount=application.loan_request.requested_amount,
            currency=application.loan_request.currency,
            tenure_months=application.loan_request.tenure_months,
            purpose=application.loan_request.purpose,
            proposed_interest_rate=application.loan_request.proposed_interest_rate,
        ),
        financials=FinancialProfileData(
            annual_revenue=_dec(revenue), previous_annual_revenue=_dec(_value(financial, 'previous_revenue')),
            ebitda=_dec(_value(financial, 'ebitda')), net_profit=_dec(_value(financial, 'net_profit')),
            cash_balance=_dec(_value(financial, 'cash_balance')), current_assets=_dec(_value(financial, 'current_assets')),
            current_liabilities=_dec(_value(financial, 'current_liabilities')), total_assets=_dec(_value(financial, 'total_assets')),
            total_liabilities=_dec(_value(financial, 'total_liabilities')), receivables=_dec(_value(financial, 'receivables')),
            inventory=_dec(_value(financial, 'inventory')), equity=_dec(_value(financial, 'equity')),
        ),
        existing_debt=DebtProfile(
            total_outstanding=total_debt, monthly_obligation=monthly_obligation,
            disclosed_facilities=int(_value(credit, 'active_facilities')) if _value(credit, 'active_facilities') is not None else None,
            observed_lender_payments=int(_value(bank, 'observed_lender_payments')) if _value(bank, 'observed_lender_payments') is not None else None,
        ),
        banking=BankingProfile(
            average_monthly_balance=_dec(_value(bank, 'average_monthly_balance')),
            minimum_balance=_dec(_value(bank, 'minimum_balance')),
            average_monthly_inflow=_dec(_value(bank, 'average_monthly_inflow')),
            average_monthly_outflow=_dec(_value(bank, 'average_monthly_outflow')),
            negative_balance_days=int(_value(bank, 'negative_balance_days')) if _value(bank, 'negative_balance_days') is not None else None,
            bounced_transactions=int(_value(bank, 'bounced_transactions')) if _value(bank, 'bounced_transactions') is not None else None,
        ),
        credit=CreditProfile(
            bureau_score=int(_value(credit, 'bureau_score')) if _value(credit, 'bureau_score') is not None else None,
            active_facilities=int(_value(credit, 'active_facilities')) if _value(credit, 'active_facilities') is not None else None,
            total_outstanding=_dec(_value(credit, 'total_outstanding_debt')),
            monthly_obligation=_dec(_value(credit, 'total_monthly_obligation')),
            delinquencies_12m=int(_value(credit, 'delinquencies_12m')) if _value(credit, 'delinquencies_12m') is not None else None,
            serious_defaults=int(_value(credit, 'serious_defaults')) if _value(credit, 'serious_defaults') is not None else None,
            hard_enquiries_6m=int(_value(credit, 'hard_enquiries_6m')) if _value(credit, 'hard_enquiries_6m') is not None else None,
            utilization_percentage=_dec(_value(credit, 'utilization_percentage')),
        ),
        collateral=CollateralProfile(
            collateral_type=_value(collateral, 'collateral_type'), owner_name=_value(collateral, 'owner_name'),
            estimated_value=_dec(_value(collateral, 'estimated_value')), encumbrance=_value(collateral, 'encumbrance'),
            valuation_date=str(_value(collateral, 'valuation_date')) if _value(collateral, 'valuation_date') else None,
        ),
        evidence_ids=[f'{ex.document_id}:{field}' for ex in extractions for field in ex.fields],
    )
