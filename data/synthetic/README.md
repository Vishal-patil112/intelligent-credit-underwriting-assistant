# Synthetic Underwriting Cases

All files in this folder are fictional and generated for hackathon/testing purposes. They contain no real customer information.

Each case has:

- `manifest.json` — sample application form payload and intended behavior
- bank statement
- financial statement
- tax return when applicable
- credit report
- existing-loan statement
- collateral document

Cases:

- `strong_case`
- `borderline_case`
- `revenue_mismatch_case`
- `serious_delinquency_case`
- `high_leverage_case`
- `weak_cashflow_case`
- `stale_collateral_case`
- `missing_tax_return_case`

Run one:

```bash
python scripts/run_case_demo.py revenue_mismatch_case
```

Run the multi-case evaluation:

```bash
python evaluate.py
```
