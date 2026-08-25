# Setup and Troubleshooting

## Recommended local software

| Software | Required? | Why |
|---|---|---|
| Git | Recommended | Commit/push the repository |
| Python 3.11 or 3.12 | Required for non-Docker setup | Backend, tests, dashboard |
| Docker Desktop / Docker Engine | Optional but easiest | Runs API, PostgreSQL, Streamlit and Tesseract together |
| Tesseract OCR | Only for local scanned image/PDF OCR | OCR fallback |
| VS Code / PyCharm | Optional | Development |
| Google AI Studio Gemini API key | Optional for deterministic demo; recommended for hackathon AI path | Gemini classification/extraction/memo |

## Option A: Windows local setup

1. Install Python 3.11/3.12. During Windows installer setup, select **Add Python to PATH**.
2. Optional: install Git.
3. Optional for scanned documents: install Tesseract OCR.
4. Extract this repository.
5. Open PowerShell in the repository folder.

Run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\setup_windows.ps1
```

Manual equivalent:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python scripts\doctor.py
pytest -q
```

Edit `.env`:

```env
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-3.5-flash-lite
```

If Tesseract is installed but not on PATH:

```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

Start API:

```powershell
.\scripts\run_api.ps1
```

Start UI in another PowerShell:

```powershell
.\scripts\run_ui.ps1
```

## Option B: Docker setup

Docker is the simplest approach because the image already installs Tesseract and Compose starts PostgreSQL.

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Services:

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- UI: http://localhost:8501
- PostgreSQL: localhost:5432

Stop:

```bash
docker compose down
```

Reset Postgres volume too:

```bash
docker compose down -v
```

## Option C: Linux/macOS

```bash
chmod +x scripts/setup_unix.sh
./scripts/setup_unix.sh
```

OCR system dependency:

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS/Homebrew
brew install tesseract
```

## Smoke tests

```bash
python scripts/doctor.py
pytest -q
python scripts/run_e2e_demo.py
python evaluate.py
```

## Gemini connectivity

After adding `GEMINI_API_KEY` to `.env`:

```bash
python scripts/check_gemini.py
```

If the account/model quota is unavailable, the main synthetic demo can still use its deterministic fallback when `LLM_FALLBACK_ENABLED=true`.

## Common issues

### `python` not found

Install Python 3.11/3.12 and reopen the terminal. On some Unix systems use `python3`.

### PowerShell activation blocked

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### `tesseract is not installed or it's not in your PATH`

Install Tesseract, then restart the terminal. On Windows you may set `TESSERACT_CMD` in `.env`.

### Port 8000 already in use

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8001
```

Then start Streamlit and set its FastAPI URL to `http://localhost:8001` in the sidebar.

### Port 8501 already in use

```powershell
.\.venv\Scripts\python.exe -m streamlit run frontend\streamlit_app.py --server.port 8502
```

### Reset local SQLite database

Stop the API and delete:

```text
data/underwriting.db
```

It is automatically recreated on startup.

### Clean uploaded demo files

Delete application subfolders under:

```text
data/uploads/
```

Keep `.gitkeep`.
