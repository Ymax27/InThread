"""Fabrique d'application FastAPI : `create_app()` assemble tout.

Ordre des middlewares (le dernier ajouté est le plus externe) :

    TrustedHostMiddleware   -> refuse les hôtes inconnus (ALLOWED_HOSTS)
      SecurityHeaders       -> CSP, nosniff, HSTS en production, cache /static
        GZipMiddleware      -> compression des réponses assez lourdes
          LiteModeMiddleware-> calcule `request.state.lite`, pose le cookie
            routeur

Ce schéma est le vrai « squelette » du projet : tout ce qui s'ajoute plus tard
(routeur, middleware, gestionnaire) se branche ici.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app import __version__
from app.config import get_settings
from app.lite import LiteModeMiddleware
from app.logging import configure_logging
from app.routes import health, pages
from app.security.headers import SecurityHeadersMiddleware, apply_security_headers
from app.templating import APP_DIR, render

log = logging.getLogger(__name__)

STATIC_DIR = APP_DIR / "static"


def _json_request(request: Request) -> bool:
    """Vrai si le client attend du JSON (API) plutôt que du HTML."""
    accept = request.headers.get("accept", "")
    return request.url.path == "/healthz" or accept.startswith("application/json")


async def _http_exception_handler(request: Request, exc: StarletteHTTPException):
    """404 et autres erreurs HTTP : page HTML propre, JSON pour les clients JSON."""
    if _json_request(request):
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
    template = "errors/404.html" if exc.status_code == 404 else "errors/error.html"
    context = {"status_code": exc.status_code, "detail": str(exc.detail)}
    return render(request, template, context, status_code=exc.status_code)


async def _unhandled_exception_handler(request: Request, exc: Exception) -> HTMLResponse:
    """500 : page générique, aucune trace d'exception exposée (seulement journalisée)."""
    log.error(
        "Erreur non gérée sur %s %s : %s",
        request.method,
        request.url.path,
        type(exc).__name__,
        exc_info=exc,
    )
    response = render(request, "errors/500.html", status_code=500)
    # Ce gestionnaire tourne hors du middleware d'en-têtes : on les pose à la main.
    apply_security_headers(response, is_production=get_settings().is_production)
    return response


def create_app() -> FastAPI:
    """Construit l'application. Testée dans tests/ (pytest + ASGITransport)."""
    settings = get_settings()
    configure_logging(settings)
    production = settings.is_production

    app = FastAPI(
        title=settings.project_name,
        version=__version__,
        debug=False,
        # Documentation interactive coupée en production (§7).
        docs_url=None if production else "/docs",
        redoc_url=None if production else "/redoc",
        openapi_url=None if production else "/openapi.json",
    )

    app.mount("/static", StaticFiles(directory=STATIC_DIR, check_dir=False), name="static")

    # Du plus interne au plus externe (inversement à l'ordre des appels).
    app.add_middleware(LiteModeMiddleware, secure_cookies=settings.session_cookie_secure)
    app.add_middleware(GZipMiddleware, minimum_size=500)
    app.add_middleware(SecurityHeadersMiddleware, is_production=production)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.hosts)

    app.include_router(health.router)
    app.include_router(pages.router)
    if not production:
        # Planche de design interne : jamais publiée en production.
        app.include_router(pages.design_router)

    app.add_exception_handler(StarletteHTTPException, _http_exception_handler)
    app.add_exception_handler(Exception, _unhandled_exception_handler)
    return app
