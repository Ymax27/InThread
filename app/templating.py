"""Rendu des pages Jinja2.

Une seule fonction `render()` gère la règle du §8 : si la requête vient de HTMX
(en-tête `HX-Request`), on ne renvoie que le fragment `partial` ; sinon la page
complète. Toutes les pages passent par là, donc le mode léger et le nom du
projet sont injectés partout sans y penser.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from app import __version__
from app.config import get_settings

APP_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(directory=APP_DIR / "templates")


def _base_context(request: Request) -> dict[str, Any]:
    """Contexte commun à tous les templates."""
    settings = get_settings()
    return {
        "request": request,
        "project_name": settings.project_name,
        "app_version": __version__,
        # Positionné par le middleware mode léger (app/lite.py).
        "lite": getattr(request.state, "lite", False),
        "current_year": datetime.now(UTC).year,
    }


def render(
    request: Request,
    template: str,
    context: dict[str, Any] | None = None,
    *,
    partial: str | None = None,
    status_code: int = 200,
) -> HTMLResponse:
    """Affiche `template` (page complète) ou `partial` si la requête vient de HTMX."""
    ctx = _base_context(request)
    if context:
        ctx.update(context)
    is_htmx = bool(request.headers.get("HX-Request"))
    name = partial if (partial and is_htmx) else template
    return templates.TemplateResponse(request, name, ctx, status_code=status_code)
