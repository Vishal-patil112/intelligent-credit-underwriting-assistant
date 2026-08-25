# Architecture

## Design principles

1. LLMs perform document understanding and explanation, not authoritative credit arithmetic.
2. Financial metrics use deterministic Python formulas.
3. Credit policy is versioned/configurable outside prompts.
4. Risk scoring is transparent and explainable.
5. Cross-document conflicts are surfaced instead of silently overwritten.
6. Important extracted values retain evidence references.
7. High-impact outcomes remain subject to human review.
8. Workflow execution is explicit through LangGraph rather than an unrestricted agent loop.

## Main components

- **FastAPI** — application/document/analysis/review APIs.
- **LangGraph** — workflow state and orchestration.
- **Document service** — PyMuPDF for digital PDFs and Tesseract OCR fallback.
- **Document classifier** — deterministic clues first, Gemini fallback.
- **Extraction agent** — Gemini JSON extraction with allowed-field constraints; deterministic key/value fallback.
- **Profile service** — merges validated extractions into a canonical borrower profile.
- **Financial service** — EMI and ratio calculations.
- **Reconciliation service** — revenue/debt/collateral/data-quality checks.
- **Risk service** — transparent points scorecard.
- **Policy service** — versioned YAML credit rules.
- **Recommendation service** — deterministic status routing plus Gemini-grounded memo text.
- **SQLAlchemy** — SQLite/PostgreSQL persistence.
- **Streamlit** — hackathon underwriter dashboard.

## State boundary

Raw documents are not handed directly to a model for a final decision. The graph progressively transforms them into structured, validated state and then applies deterministic calculations and policy.

## Persistence

Local:

```text
SQLite -> data/underwriting.db
Documents -> data/uploads/<application_id>/
```

Docker:

```text
PostgreSQL container + mounted upload directory
```

For production scale, local document storage should be replaced by an approved object store and database migration tooling should be introduced.
