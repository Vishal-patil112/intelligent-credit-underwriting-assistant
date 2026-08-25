$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot
$PythonExe = "$RepoRoot\.venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) { throw "Run scripts\setup_windows.ps1 first." }
& $PythonExe -m pytest -q
& $PythonExe scripts\run_e2e_demo.py
& $PythonExe evaluate.py
Write-Host "VALIDATION_OK" -ForegroundColor Green
