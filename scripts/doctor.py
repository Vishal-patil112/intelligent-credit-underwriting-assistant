"""Local environment checks. This script does not call Gemini or modify data."""
from __future__ import annotations

import importlib
import platform
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

REQUIRED_IMPORTS = {
    "fastapi": "FastAPI",
    "uvicorn": "Uvicorn",
    "pydantic": "Pydantic",
    "langgraph": "LangGraph",
    "google.genai": "Google GenAI SDK",
    "pymupdf": "PyMuPDF",
    "PIL": "Pillow",
    "pytesseract": "pytesseract",
    "sqlalchemy": "SQLAlchemy",
    "streamlit": "Streamlit",
}


def mark(ok: bool) -> str:
    return "OK" if ok else "MISSING"


def main() -> int:
    print("Environment doctor")
    print("-" * 72)
    print(f"Python: {sys.version.split()[0]} ({platform.system()} {platform.release()})")
    python_ok = sys.version_info >= (3, 11)
    print(f"Python >= 3.11: {mark(python_ok)}")

    imports_ok = True
    for module, label in REQUIRED_IMPORTS.items():
        try:
            importlib.import_module(module)
            ok = True
        except Exception:
            ok = False
            imports_ok = False
        print(f"{label}: {mark(ok)}")

    env_path = ROOT / ".env"
    print(f".env present: {mark(env_path.exists())}")
    print(f"credit_policy.yaml: {mark((ROOT / 'config' / 'credit_policy.yaml').exists())}")
    print(f"risk_scorecard.yaml: {mark((ROOT / 'config' / 'risk_scorecard.yaml').exists())}")

    try:
        from app.config import get_settings
        settings = get_settings()
        tesseract_env = (settings.tesseract_cmd or "").strip()
        key_present = settings.gemini_configured
    except Exception:
        tesseract_env = ""
        key_present = False
    tesseract_ok = bool((tesseract_env and Path(tesseract_env).exists()) or shutil.which("tesseract"))
    print(f"Tesseract executable (needed only for scanned images/PDFs): {mark(tesseract_ok)}")
    if not tesseract_ok:
        print("  Note: digital PDFs and bundled text demo still work without Tesseract.")
        print("  Windows: install Tesseract OCR and add it to PATH, or set TESSERACT_CMD in .env.")
        print("  Ubuntu/Debian: sudo apt-get install tesseract-ocr")
        print("  macOS/Homebrew: brew install tesseract")

    print(f"GEMINI_API_KEY configuration: {'SET' if key_present else 'NOT SET (deterministic demo still works)'}")

    overall = python_ok and imports_ok
    print("-" * 72)
    print("Core environment:", "READY" if overall else "NOT READY")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
