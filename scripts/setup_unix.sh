#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "== Intelligent Credit Underwriting Assistant: Unix setup =="

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 was not found. Install Python 3.11+ first." >&2
  exit 1
fi

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

PY="$REPO_ROOT/.venv/bin/python"
"$PY" -m pip install --upgrade pip
"$PY" -m pip install -r requirements.txt

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

"$PY" scripts/doctor.py
"$PY" -m pytest -q

echo
echo "Setup complete."
echo "API: $PY -m uvicorn app.main:app --reload --port 8000"
echo "UI:  $PY -m streamlit run frontend/streamlit_app.py"
