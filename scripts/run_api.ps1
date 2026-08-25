$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot
& "$RepoRoot\.venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
