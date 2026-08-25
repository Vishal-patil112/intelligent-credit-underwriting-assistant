"""Generate deterministic synthetic underwriting document packs for demo/evaluation.

No real customer information is used. Re-running the script replaces only the known
sample case directories under data/synthetic.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "synthetic"


def write_case(name: str, manifest: dict, docs: dict[str, str]) -> None:
    folder = BASE / name
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob("*"):
        if old.is_file():
            old.unlink()
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    for filename, content in docs.items():
        (folder / filename).write_text(content.strip() + "\n", encoding="utf-8")


def common_docs(*, business: str, revenue: int, previous: int, ebitda: int, net_profit: int,
                current_assets: int, current_liabilities: int, total_debt: int,
                inflow: int, outflow: int, avg_balance: int, bounces: int,
                bureau: int, serious_defaults: int, active_facilities: int,
                credit_debt: int, monthly_obligation: int, tax_turnover: int,
                collateral_value: int, valuation_date: str, observed_lenders: int = 2) -> dict[str, str]:
    return {
        "bank_statement.txt": f"""BANK STATEMENT
Account Holder: {business}
Account Number Masked: XXXX1234
Bank Name: Demo Business Bank
Opening Balance: {avg_balance}
Closing Balance: {avg_balance}
Average Monthly Inflow: {inflow}
Average Monthly Outflow: {outflow}
Average Monthly Balance: {avg_balance}
Minimum Balance: {max(avg_balance // 2, 0)}
Negative Balance Days: 0
Bounced Transactions: {bounces}
Recurring EMI: {monthly_obligation}
Observed Lender Payments: {observed_lenders}
""",
        "financial_statement.txt": f"""FINANCIAL STATEMENT
Business Name: {business}
Revenue: {revenue}
Previous Revenue: {previous}
EBITDA: {ebitda}
Net Profit: {net_profit}
Cash Balance: {avg_balance}
Current Assets: {current_assets}
Current Liabilities: {current_liabilities}
Total Assets: {current_assets * 2}
Total Liabilities: {current_liabilities + total_debt}
Total Debt: {total_debt}
Receivables: {revenue // 8}
Inventory: {revenue // 10}
Equity: {max(current_assets * 2 - current_liabilities - total_debt, 0)}
""",
        "tax_return.txt": f"""TAX RETURN
Business Name: {business}
Tax Identifier: DEMO-TAX-001
Reported Turnover: {tax_turnover}
Taxable Income: {max(net_profit, 0)}
Tax Paid: {max(net_profit // 5, 0)}
Filing Date: 2026-07-31
""",
        "credit_report.txt": f"""CREDIT REPORT
Bureau Score: {bureau}
Active Facilities: {active_facilities}
Total Outstanding Debt: {credit_debt}
Total Monthly Obligation: {monthly_obligation}
Delinquencies 12m: {1 if serious_defaults else 0}
Serious Defaults: {serious_defaults}
Hard Enquiries 6m: 1
Utilization Percentage: 30
""",
        "existing_loan_statement.txt": f"""EXISTING LOAN STATEMENT
Lender: Demo Commercial Bank
Loan Type: Equipment Loan
Outstanding Principal: {credit_debt}
EMI: {monthly_obligation}
Total Outstanding: {credit_debt}
Total Monthly Obligation: {monthly_obligation}
Days Past Due: {30 if serious_defaults else 0}
""",
        "collateral_document.txt": f"""COLLATERAL DOCUMENT
Collateral Type: Commercial Property
Asset Description: Synthetic demo business asset
Owner Name: {business}
Estimated Value: {collateral_value}
Encumbrance: false
Valuation Date: {valuation_date}
""",
    }


def manifest(business: str, *, vintage: int, declared_revenue: int, declared_debt: int,
             amount: int = 5_000_000, rate: float = 11.5, expected: str) -> dict:
    return {
        "description": expected,
        "application": {
            "business_name": business,
            "business_type": "PRIVATE_LIMITED",
            "industry": "Manufacturing",
            "business_vintage_years": vintage,
            "registration_number": "DEMO-REG-001",
            "tax_identifier": "DEMO-TAX-001",
            "declared_annual_revenue": declared_revenue,
            "declared_existing_obligations": declared_debt,
            "loan_request": {
                "requested_amount": amount,
                "currency": "INR",
                "tenure_months": 60,
                "purpose": "Purchase of machinery",
                "proposed_interest_rate": rate,
                "collateral_offered": True,
            },
            "consent_confirmed": True,
        },
        "expected_behavior": expected,
    }


def main() -> None:
    BASE.mkdir(parents=True, exist_ok=True)

    business = "ABC Manufacturing Pvt Ltd"
    strong = common_docs(business=business, revenue=35_000_000, previous=32_000_000, ebitda=8_000_000,
        net_profit=4_200_000, current_assets=12_000_000, current_liabilities=6_000_000, total_debt=4_000_000,
        inflow=2_900_000, outflow=2_450_000, avg_balance=1_500_000, bounces=0, bureau=760,
        serious_defaults=0, active_facilities=2, credit_debt=4_000_000, monthly_obligation=120_000,
        tax_turnover=34_800_000, collateral_value=8_000_000, valuation_date="2026-06-30")
    write_case("strong_case", manifest(business, vintage=7, declared_revenue=35_000_000, declared_debt=4_000_000,
        expected="Strong borrower; expected APPROVE under illustrative policy."), strong)

    borderline = common_docs(business="Borderline Industries Pvt Ltd", revenue=24_000_000, previous=23_000_000, ebitda=3_500_000,
        net_profit=1_500_000, current_assets=6_600_000, current_liabilities=6_000_000, total_debt=12_000_000,
        inflow=2_000_000, outflow=1_850_000, avg_balance=700_000, bounces=2, bureau=680,
        serious_defaults=0, active_facilities=3, credit_debt=12_000_000, monthly_obligation=160_000,
        tax_turnover=23_800_000, collateral_value=8_500_000, valuation_date="2026-06-30")
    write_case("borderline_case", manifest("Borderline Industries Pvt Ltd", vintage=4, declared_revenue=24_000_000, declared_debt=12_000_000,
        amount=3_000_000, expected="Borderline-but-policy-compliant profile; typically CONDITIONAL_APPROVE depending calculated risk."), borderline)

    mismatch = common_docs(business="Mismatch Trading Pvt Ltd", revenue=30_000_000, previous=28_000_000, ebitda=7_000_000,
        net_profit=3_500_000, current_assets=11_000_000, current_liabilities=5_000_000, total_debt=3_500_000,
        inflow=1_800_000, outflow=1_400_000, avg_balance=1_200_000, bounces=0, bureau=755,
        serious_defaults=0, active_facilities=2, credit_debt=3_500_000, monthly_obligation=100_000,
        tax_turnover=17_000_000, collateral_value=9_000_000, valuation_date="2026-06-30")
    write_case("revenue_mismatch_case", manifest("Mismatch Trading Pvt Ltd", vintage=6, declared_revenue=40_000_000, declared_debt=3_500_000,
        amount=4_000_000, expected="Material revenue discrepancy; expected MANUAL_REVIEW due to high-severity anomaly if policy otherwise passes."), mismatch)

    delinquent = common_docs(business="Delinquent Services Pvt Ltd", revenue=28_000_000, previous=27_000_000, ebitda=6_000_000,
        net_profit=3_000_000, current_assets=10_000_000, current_liabilities=5_000_000, total_debt=4_000_000,
        inflow=2_300_000, outflow=1_900_000, avg_balance=1_000_000, bounces=1, bureau=620,
        serious_defaults=1, active_facilities=3, credit_debt=4_000_000, monthly_obligation=130_000,
        tax_turnover=27_800_000, collateral_value=8_000_000, valuation_date="2026-06-30")
    write_case("serious_delinquency_case", manifest("Delinquent Services Pvt Ltd", vintage=5, declared_revenue=28_000_000, declared_debt=4_000_000,
        expected="Serious default / sub-policy credit score; expected REJECT under illustrative hard policy."), delinquent)

    high_lev = common_docs(business="Leveraged Engineering Pvt Ltd", revenue=32_000_000, previous=31_000_000, ebitda=3_000_000,
        net_profit=1_600_000, current_assets=9_000_000, current_liabilities=7_000_000, total_debt=15_000_000,
        inflow=2_600_000, outflow=2_350_000, avg_balance=800_000, bounces=1, bureau=710,
        serious_defaults=0, active_facilities=4, credit_debt=15_000_000, monthly_obligation=280_000,
        tax_turnover=31_500_000, collateral_value=10_000_000, valuation_date="2026-06-30")
    write_case("high_leverage_case", manifest("Leveraged Engineering Pvt Ltd", vintage=5, declared_revenue=32_000_000, declared_debt=15_000_000,
        expected="Debt/EBITDA above policy maximum and weak DSCR; expected REJECT under illustrative policy."), high_lev)

    weak_cash = common_docs(business="Weak Cashflow Retail Pvt Ltd", revenue=20_000_000, previous=21_000_000, ebitda=2_000_000,
        net_profit=700_000, current_assets=5_000_000, current_liabilities=5_500_000, total_debt=5_000_000,
        inflow=1_500_000, outflow=1_550_000, avg_balance=300_000, bounces=4, bureau=690,
        serious_defaults=0, active_facilities=2, credit_debt=5_000_000, monthly_obligation=180_000,
        tax_turnover=19_700_000, collateral_value=7_000_000, valuation_date="2026-06-30")
    write_case("weak_cashflow_case", manifest("Weak Cashflow Retail Pvt Ltd", vintage=3, declared_revenue=20_000_000, declared_debt=5_000_000,
        expected="Weak repayment capacity and repeated bounces; expected policy failure or elevated manual/reject outcome."), weak_cash)

    stale = common_docs(business="Stable Collateral Pvt Ltd", revenue=30_000_000, previous=29_000_000, ebitda=6_500_000,
        net_profit=3_300_000, current_assets=10_500_000, current_liabilities=5_500_000, total_debt=4_000_000,
        inflow=2_500_000, outflow=2_000_000, avg_balance=1_100_000, bounces=0, bureau=745,
        serious_defaults=0, active_facilities=2, credit_debt=4_000_000, monthly_obligation=110_000,
        tax_turnover=29_800_000, collateral_value=8_000_000, valuation_date="2024-01-15")
    write_case("stale_collateral_case", manifest("Stable Collateral Pvt Ltd", vintage=6, declared_revenue=30_000_000, declared_debt=4_000_000,
        expected="Otherwise strong borrower with stale collateral valuation; expected anomaly requiring human verification."), stale)

    missing = common_docs(business="Incomplete Foods Pvt Ltd", revenue=26_000_000, previous=24_000_000, ebitda=5_500_000,
        net_profit=2_800_000, current_assets=9_000_000, current_liabilities=5_000_000, total_debt=3_500_000,
        inflow=2_200_000, outflow=1_850_000, avg_balance=950_000, bounces=0, bureau=740,
        serious_defaults=0, active_facilities=2, credit_debt=3_500_000, monthly_obligation=100_000,
        tax_turnover=25_800_000, collateral_value=7_500_000, valuation_date="2026-06-30")
    missing.pop("tax_return.txt")
    write_case("missing_tax_return_case", manifest("Incomplete Foods Pvt Ltd", vintage=5, declared_revenue=26_000_000, declared_debt=3_500_000,
        expected="Required TAX_RETURN missing; expected REQUEST_MORE_DOCUMENTS / INCOMPLETE."), missing)

    print(f"Generated 8 synthetic cases under {BASE}")


if __name__ == "__main__":
    main()
