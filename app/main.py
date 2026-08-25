"""FastAPI application for the complete end-to-end underwriting hackathon repository."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api import applications_router, documents_router, review_router, underwriting_router
from app.config import get_settings
from app.db.session import SessionLocal, init_db
from app.logging_config import configure_logging, request_id_ctx

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.ensure_runtime_directories()
    init_db()
    logger.info('application_started')
    yield
    logger.info('application_stopped')


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        'End-to-end LangGraph small-business credit underwriting assistant: application/document intake, '
        'OCR/PDF parsing, Gemini-assisted extraction, deterministic financial/risk/policy engines, '
        'evidence-backed recommendation, what-if simulation, human review and audit.'
    ),
    lifespan=lifespan,
)


@app.middleware('http')
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get('X-Request-ID') or str(uuid4())
    token = request_id_ctx.set(request_id)
    try:
        response = await call_next(request)
        response.headers['X-Request-ID'] = request_id
        return response
    finally:
        request_id_ctx.reset(token)


app.include_router(applications_router)
app.include_router(documents_router)
app.include_router(underwriting_router)
app.include_router(review_router)


@app.get('/', tags=['system'])
def root() -> dict[str, str]:
    return {'service': settings.app_name, 'version': settings.app_version, 'release': 'master-e2e', 'docs': '/docs'}


@app.get('/health', tags=['system'])
def health() -> dict[str, str]:
    return {'status': 'ok', 'service': settings.app_name, 'version': settings.app_version}


@app.get('/ready', tags=['system'])
def readiness() -> JSONResponse:
    settings.ensure_runtime_directories()
    db_ok = False
    try:
        with SessionLocal() as db:
            db.execute(text('SELECT 1'))
            db_ok = True
    except Exception:
        db_ok = False
    checks = {
        'database': db_ok,
        'upload_directory_writable': _directory_writable(settings.upload_directory),
        'credit_policy_config_present': settings.credit_policy_path.is_file(),
        'risk_scorecard_config_present': settings.risk_scorecard_path.is_file(),
        'gemini_configured': settings.gemini_configured,
        'llm_fallback_enabled': settings.llm_fallback_enabled,
    }
    required_ok = all(checks[name] for name in ('database', 'upload_directory_writable', 'credit_policy_config_present', 'risk_scorecard_config_present'))
    payload = {'status': 'ready' if required_ok else 'not_ready', 'release': 'master-e2e', 'checks': checks}
    return JSONResponse(status_code=200 if required_ok else 503, content=payload)


def _directory_writable(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / '.write_probe'; probe.write_text('ok', encoding='utf-8'); probe.unlink(missing_ok=True)
        return True
    except OSError:
        return False
