"""En-têtes de sécurité posés sur toutes les réponses (§7)."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

# Aucun script ni style inline : c'est ce qui interdit `onclick=`, `<script>` dans
# le HTML et `hx-on` dans HTMX. Les ressources viennent de `self` uniquement.
CSP = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self'; "
    "img-src 'self' data:; "
    "font-src 'self'; "
    "connect-src 'self'; "
    "object-src 'none'; "
    "base-uri 'self'; "
    "form-action 'self'; "
    "frame-ancestors 'none'"
)

PERMISSIONS_POLICY = (
    "accelerometer=(), camera=(), geolocation=(), gyroscope=(), microphone=(), payment=(), usb=()"
)

HSTS = "max-age=31536000; includeSubDomains"

# Cache long sur les ressources statiques : les URLs portent un paramètre de
# version (`/static/css/app.css?v=0.1.0`), donc nouveau fichier = nouvelle URL.
CACHE_STATIQUE = "public, max-age=604800"


def apply_security_headers(response: Response, *, is_production: bool, path: str = "") -> None:
    """Pose les en-têtes de sécurité sur une réponse (muté en place)."""
    headers = response.headers
    headers.setdefault("Content-Security-Policy", CSP)
    headers.setdefault("X-Content-Type-Options", "nosniff")
    headers.setdefault("X-Frame-Options", "DENY")
    headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    headers.setdefault("Permissions-Policy", PERMISSIONS_POLICY)
    if path.startswith("/static/"):
        headers.setdefault("Cache-Control", CACHE_STATIQUE)
    if is_production:
        # Uniquement en HTTPS : en local, HSTS forcerait https:// sur localhost.
        headers.setdefault("Strict-Transport-Security", HSTS)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Ajoute les en-têtes de sécurité à chaque réponse (y compris les erreurs 4xx).

    La page 500 est produite par le gestionnaire d'exception global, hors de ce
    middleware : celui-ci rappelle alors `apply_security_headers` lui-même.
    """

    def __init__(self, app: ASGIApp, *, is_production: bool) -> None:
        super().__init__(app)
        self.is_production = is_production

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        apply_security_headers(response, is_production=self.is_production, path=request.url.path)
        return response
