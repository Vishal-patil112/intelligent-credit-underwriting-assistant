#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PY="$ROOT/.venv/bin/python"
if [ ! -x "$PY" ]; then
  echo "Run scripts/setup_unix.sh first." >&2
  exit 1
fi
"$PY" -m pytest -q
"$PY" scripts/run_e2e_demo.py
"$PY" evaluate.py
echo "VALIDATION_OK"
