$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

Write-Host "== Intelligent Credit Underwriting Assistant: Windows setup ==" -ForegroundColor Cyan

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python was not found. Install Python 3.11 or 3.12 and reopen PowerShell."
}

$versionText = python --version
Write-Host $versionText

if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

$PythonExe = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    throw "Virtual environment Python was not created correctly."
}

Write-Host "Upgrading pip..."
& $PythonExe -m pip install --upgrade pip

Write-Host "Installing dependencies..."
& $PythonExe -m pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example" -ForegroundColor Green
} else {
    Write-Host ".env already exists - leaving it unchanged."
}

Write-Host "Running environment doctor..."
& $PythonExe scripts\doctor.py

Write-Host "Running tests..."
& $PythonExe -m pytest -q

Write-Host ""
Write-Host "Setup complete." -ForegroundColor Green
Write-Host "Next:"
Write-Host "  1) Edit .env and add GEMINI_API_KEY if you want Gemini calls."
Write-Host "  2) Run: .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"
Write-Host "  3) In another terminal: .\.venv\Scripts\python.exe -m streamlit run frontend\streamlit_app.py"
Write-Host "  4) Swagger: http://localhost:8000/docs"
Write-Host "  5) UI:      http://localhost:8501"
