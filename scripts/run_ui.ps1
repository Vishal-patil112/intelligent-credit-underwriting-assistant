$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot
& "$RepoRoot\.venv\Scripts\python.exe" -m streamlit run frontend\streamlit_app.py --server.port 8501
