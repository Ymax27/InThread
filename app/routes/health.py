"""`GET /healthz` : JSON, utilisé par Docker HEALTHCHECK, la CI et Datacloud."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app import __version__
from app.config import get_settings
from app.db import database_reachable

router = APIRouter(tags=["santé"])


@router.get("/healthz", include_in_schema=False)
async def healthz() -> JSONResponse:
    """200 si la base répond dans les temps, 503 sinon (jamais d'exception)."""
    settings = get_settings()
    db_ok = await database_reachable(settings.db_timeout_seconds)
    return JSONResponse(
        {
            "status": "ok" if db_ok else "error",
            "db": "ok" if db_ok else "error",
            "version": __version__,
        },
        status_code=200 if db_ok else 503,
    )
