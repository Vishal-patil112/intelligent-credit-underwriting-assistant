"""Structured JSON logging and request correlation utilities."""

from __future__ import annotations

import contextvars
import json
import logging
from datetime import datetime, timezone


request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default="-"
)
application_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    "application_id", default="-"
)


class JsonFormatter(logging.Formatter):
    """Small dependency-free JSON formatter for hackathon observability."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_ctx.get(),
            "application_id": application_id_ctx.get(),
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def configure_logging(level: str = "INFO") -> None:
    """Configure root logging once using JSON output."""
    root = logging.getLogger()
    root.setLevel(level.upper())

    # Uvicorn may install handlers before app startup. Replace them so logs are
    # consistent when run locally and in Docker.
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root.handlers.clear()
    root.addHandler(handler)

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.propagate = True
