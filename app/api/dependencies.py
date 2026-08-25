from __future__ import annotations

from collections.abc import AsyncGenerator

from app.logging_config import application_id_ctx


async def bind_application_id(
    application_id: str,
) -> AsyncGenerator[None, None]:
    """Bind the application ID to the current request logging context.

    Using an async generator dependency is important here because ContextVar
    tokens must be reset in the same context in which they were created.
    """

    token = application_id_ctx.set(application_id)

    try:
        yield
    finally:
        application_id_ctx.reset(token)