$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot
& "$RepoRoot\.venv\Scripts\python.exe" scripts\run_e2e_demo.py
