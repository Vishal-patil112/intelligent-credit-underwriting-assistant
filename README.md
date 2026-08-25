# Intelligent Small Business Credit Underwriting Assistant

End-to-end, hackathon-ready **Agentic AI small-business loan underwriting assistant** built with **LangGraph, Google Gemini, FastAPI, Pydantic, deterministic financial analysis, configurable credit policy, explainable risk scoring, Streamlit, SQLAlchemy, OCR, and human-in-the-loop review**.

> **Design rule:** AI understands and explains. Python calculates. Policy controls. A human underwriter makes the consequential final decision.

This repository is intentionally production-inspired but hackathon-sized. It is not a real bank credit policy implementation and must not be used to make real lending decisions without institution-specific validation, governance, security, regulatory, and model-risk review.

## What is included

- FastAPI backend and Swagger API
- LangGraph `StateGraph` orchestration with explicit conditional routing
- Google Gemini adapter for classification, extraction, and grounded memo writing
- Deterministic fallback path so the synthetic demo/tests work without an API key
- Digital PDF parsing with PyMuPDF
- Tesseract OCR fallback for scanned PDFs and images
- Pydantic schemas and evidence lineage
- Application and document persistence with SQLAlchemy
- SQLite for simple local setup; PostgreSQL via Docker Compose
- File upload validation, local object-storage abstraction, SHA-256 duplicate detection
- Canonical borrower financial profile
- Deterministic EMI, DSCR, Debt/EBITDA, current ratio, margin, revenue growth, net cash flow, debt burden, and LTV
- Cross-document reconciliation and anomaly detection
- YAML-configured transparent risk scorecard
- YAML-configured credit policy engine
- Deterministic recommendation routing
- Gemini-generated grounded credit memo with deterministic fallback
- Human-underwriter final decision / override workflow
- Full audit trail
- What-if loan simulator
- Streamlit underwriter dashboard
- 8 synthetic borrower scenarios
- Evaluation harness
- Pytest unit/API/end-to-end tests
- Dockerfile + Docker Compose
- Windows and Unix setup scripts
- GitHub Actions CI workflow

## Architecture

```text
Customer / Banker
      |
      v
Streamlit / FastAPI
      |
      +-------------------+
      |                   |
      v                   v
Application Data      Document Upload
                          |
                          v
                 Storage + SHA-256
                          |
                          v
                  PDF Parser / OCR
                          |
                          v
                 Document Classifier
                   Rules -> Gemini
                          |
                          v
                 Structured Extraction
                Gemini -> validated data
                          |
                          v
                 Canonical Borrower Profile
                          |
          +---------------+---------------+
          |               |               |
          v               v               v
   Financial Engine   Reconciliation   Anomalies
          |               |               |
          +---------------+---------------+
                          |
                          v
                  Risk Scorecard
                          |
                          v
                 Credit Policy Engine
                          |
                          v
                Recommendation Router
                          |
                          v
                 Grounded Credit Memo
                          |
                          v
                  Human Underwriter
                          |
                          v
                  Final Decision + Audit
```

## LangGraph flow

```text
START
  |
load_case
  |
check_documents
  |---- no docs ----> request_documents --> END
  |
classify_documents
  |
extract_documents
  |
build_financial_profile
  |
calculate_metrics
  |
anomaly_detection
  |
calculate_risk
  |
apply_policy
  |
generate_recommendation
  |
persist_analysis
  |
END
```

## Fastest setup: Docker

Prerequisite: **Docker Desktop** (Windows/macOS) or Docker Engine + Compose (Linux).

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Optionally add your Gemini key to `.env`:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
```

Start the complete stack:

```bash
docker compose up --build
```

Open:

- Streamlit: http://localhost:8501
- Swagger: http://localhost:8000/docs
- API health: http://localhost:8000/health
- API readiness: http://localhost:8000/ready

Docker installs Tesseract inside the application image automatically.

## Local Windows setup

Recommended: **Python 3.11 or 3.12**.

From PowerShell in the repository root:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\setup_windows.ps1
```

The script creates `.venv`, installs Python packages, creates `.env` if missing, runs environment checks, and runs the test suite.

Then edit `.env` if you want real Gemini calls:

```env
GEMINI_API_KEY=your_google_ai_studio_key
```

Start the API:

```powershell
.\scripts\run_api.ps1
```

In a second terminal start the UI:

```powershell
.\scripts\run_ui.ps1
```

For scanned images/PDF OCR outside Docker, install Tesseract and either add it to `PATH` or set:

```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

Digital PDFs and the bundled `.txt` synthetic demo do not require the Tesseract executable.

## Local macOS / Linux setup

```bash
chmod +x scripts/setup_unix.sh
./scripts/setup_unix.sh
```

Then:

```bash
.venv/bin/python -m uvicorn app.main:app --reload --port 8000
```

In a second terminal:

```bash
.venv/bin/python -m streamlit run frontend/streamlit_app.py
```

For scanned-image OCR:

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS/Homebrew
brew install tesseract
```

See [docs/SETUP.md](docs/SETUP.md) for the full setup/troubleshooting guide.

## Validate before using the UI

```bash
pytest -q
python scripts/doctor.py
python scripts/run_e2e_demo.py
python evaluate.py
```

The E2E demo intentionally uses synthetic data and works without Gemini by using the deterministic fallback path.

## Synthetic demo cases

The repository includes eight scenarios under `data/synthetic/`:

| Case | Intended demonstration |
|---|---|
| `strong_case` | Policy PASS / APPROVE |
| `borderline_case` | Policy PASS / CONDITIONAL_APPROVE |
| `revenue_mismatch_case` | Cross-document mismatch / MANUAL_REVIEW |
| `serious_delinquency_case` | Hard policy failure / REJECT |
| `high_leverage_case` | Leverage/DSCR policy failure / REJECT |
| `weak_cashflow_case` | Weak repayment capacity / REJECT |
| `stale_collateral_case` | Stale valuation anomaly requiring human verification |
| `missing_tax_return_case` | Missing required document / REQUEST_MORE_DOCUMENTS |

Run any case:

```bash
python scripts/run_case_demo.py strong_case
python scripts/run_case_demo.py revenue_mismatch_case
python scripts/run_case_demo.py missing_tax_return_case
```

Regenerate all bundled synthetic cases:

```bash
python scripts/generate_synthetic_cases.py
```

## API endpoints

```text
GET  /
GET  /health
GET  /ready

POST /applications
GET  /applications
GET  /applications/{application_id}

POST /applications/{application_id}/documents
GET  /applications/{application_id}/documents
GET  /applications/{application_id}/documents/{document_id}

POST /applications/{application_id}/analyze
GET  /applications/{application_id}/analysis
GET  /applications/{application_id}/profile
GET  /applications/{application_id}/metrics
GET  /applications/{application_id}/anomalies
GET  /applications/{application_id}/risk
GET  /applications/{application_id}/policy
GET  /applications/{application_id}/recommendation
GET  /applications/{application_id}/audit

POST /applications/{application_id}/simulate

POST /applications/{application_id}/decision
GET  /applications/{application_id}/decision
```

Detailed examples: [docs/API_EXAMPLES.md](docs/API_EXAMPLES.md).

## Core configuration

### `config/credit_policy.yaml`

Illustrative hackathon policy such as minimum business vintage, minimum bureau score, minimum DSCR, maximum leverage, maximum LTV, serious-default limits, and required document types.

### `config/risk_scorecard.yaml`

Transparent category weights for repayment capacity, credit behaviour, leverage, liquidity, profitability, banking behaviour, business stability, and data quality/anomalies.

These are **demo configurations only**, not real bank policy.

## LLM boundary

Gemini is used for:

- ambiguous document classification
- structured document field extraction
- grounded underwriting narrative generation

Gemini is **not** authoritative for:

- EMI or financial ratio calculation
- risk-score arithmetic
- credit policy thresholds
- deterministic anomaly rules
- final human decision

If Gemini is unavailable and `LLM_FALLBACK_ENABLED=true`, supported synthetic/key-value documents can still run through the deterministic demo path.

## Repository structure

```text
intelligent-credit-underwriting-assistant/
├── .github/workflows/ci.yml
├── app/
│   ├── agents/
│   ├── api/
│   ├── db/
│   ├── graph/
│   ├── llm/
│   ├── schemas/
│   ├── services/
│   ├── config.py
│   ├── logging_config.py
│   └── main.py
├── config/
│   ├── credit_policy.yaml
│   └── risk_scorecard.yaml
├── data/
│   ├── synthetic/
│   └── uploads/.gitkeep
├── docs/
│   ├── API_EXAMPLES.md
│   ├── ARCHITECTURE.md
│   ├── DEMO.md
│   ├── SECURITY_AND_LIMITATIONS.md
│   └── SETUP.md
├── evaluation/
│   └── ground_truth.json
├── frontend/
│   └── streamlit_app.py
├── scripts/
│   ├── check_gemini.py
│   ├── doctor.py
│   ├── generate_synthetic_cases.py
│   ├── run_case_demo.py
│   ├── run_e2e_demo.py
│   ├── setup_windows.ps1
│   └── setup_unix.sh
├── tests/
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── evaluate.py
├── pytest.ini
├── requirements-dev.txt
├── requirements.txt
└── README.md
```

## Commit to your GitHub repository

Recommended repository name:

```text
intelligent-credit-underwriting-assistant
```

After local validation:

```bash
git init
git add .
git status
git commit -m "Initial end-to-end intelligent credit underwriting assistant"
git branch -M main
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
git push -u origin main
```

Before `git add .`, confirm that `.env`, local database files, uploaded customer documents, virtual environments, caches, and logs are not staged. The included `.gitignore` excludes them.

## Security and data warning

Use **synthetic data** for the hackathon/free-tier demo. Do not upload real customer financial, tax, credit, identity, or property documents to third-party LLM services without the bank's approved privacy, data-processing, security, and regulatory controls.

See [docs/SECURITY_AND_LIMITATIONS.md](docs/SECURITY_AND_LIMITATIONS.md).
