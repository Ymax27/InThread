"""Middleware « mode léger » : expose `request.state.lite` à toute l'application.

Trois manières d'activer le mode léger (§8) :
- `?lite=1` (pose le cookie `lite=1`) et `?lite=0` (le retire),
- l'en-tête `Save-Data: on` envoyé par certains opérateurs,
- le cookie `lite=1` posé lors d'une visite précédente.

En mode léger, `base.html` ne charge ni HTMX, ni motif décoratif, et les listes
sont plus compactes.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

COOKIE_LITE = "lite"
DUREE_COOKIE_JOURS = 180


class LiteModeMiddleware(BaseHTTPMiddleware):
    """Calcule le mode léger avant la vue et repose le cookie si besoin."""

    def __init__(self, app: ASGIApp, *, secure_cookies: bool) -> None:
        super().__init__(app)
        self.secure_cookies = secure_cookies

    async def dispatch(self, request: Request, call_next) -> Response:
        demande = request.query_params.get("lite")
        pose_cookie = False
        retire_cookie = False

        if demande == "1":
            lite, pose_cookie = True, True
        elif demande == "0":
            lite, retire_cookie = False, True
        elif request.headers.get("Save-Data", "").strip().lower() == "on":
            # Forfait économe : on n'allège pas pour toujours, seulement pour cette requête.
            lite = True
        else:
            lite = request.cookies.get(COOKIE_LITE) == "1"

        # Lu par app/templating.py : `lite` est donc disponible dans tous les templates.
        request.state.lite = lite
        response = await call_next(request)

        if pose_cookie:
            response.set_cookie(
                COOKIE_LITE,
                "1",
                max_age=DUREE_COOKIE_JOURS * 24 * 3600,
                path="/",
                httponly=True,  # seulement le serveur en a besoin
                samesite="lax",
                secure=self.secure_cookies,
            )
        elif retire_cookie:
            response.delete_cookie(
                COOKIE_LITE, path="/", samesite="lax", secure=self.secure_cookies
            )
        return response
