# Hackathon Demo Guide

A good demo fits in approximately 6-8 minutes.

## 0-1 minute: problem and architecture

Explain that small-business underwriting requires repetitive review of bank, financial, tax, credit, loan and collateral documents.

Key sentence:

> AI understands the documents; deterministic Python calculates; policy controls eligibility; the human underwriter retains final authority.

## 1-2 minutes: create application and upload documents

Use Streamlit at http://localhost:8501.

Create the sample borrower and upload files from:

```text
data/synthetic/strong_case/
```

Do not upload `manifest.json`; upload the `.txt` documents only.

## 2-4 minutes: run analysis

Show:

- document classification
- unified profile
- DSCR and other financial metrics
- risk score/grade
- policy result
- recommendation
- anomalies
- evidence IDs

## 4-5 minutes: show cross-document intelligence

Run:

```bash
python scripts/run_case_demo.py revenue_mismatch_case
```

Show that a material mismatch is surfaced as an anomaly and routes the case to manual review instead of blindly accepting one number.

## 5-6 minutes: missing-document handling

```bash
python scripts/run_case_demo.py missing_tax_return_case
```

The system should return an incomplete/request-more-documents outcome.

## 6-7 minutes: what-if simulation

For a created/analyzed application, reduce loan amount and show recalculated EMI/DSCR/policy/recommendation without overwriting the original application.

## 7-8 minutes: human decision and audit

Submit an underwriter action in Streamlit and expand the audit trail.

End with:

> The LLM never independently decides who receives a loan. It reduces the document-understanding burden and produces an evidence-backed view for governed underwriting.
