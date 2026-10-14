"""Tests de `GET /healthz` : 200 avec base, 503 sans base."""

from __future__ import annotations

from httpx import AsyncClient

from app import __version__


async def test_healthz_avec_base(client: AsyncClient) -> None:
    reponse = await client.get("/healthz")
    assert reponse.status_code == 200
    assert reponse.json() == {"status": "ok", "db": "ok", "version": __version__}
    assert reponse.headers["content-type"].startswith("application/json")


async def test_healthz_sans_base_renvoie_503(client_sans_base: AsyncClient) -> None:
    reponse = await client_sans_base.get("/healthz")
    assert reponse.status_code == 503
    corps = reponse.json()
    assert corps["db"] == "error"
    assert corps["status"] == "error"
    assert corps["version"] == __version__


async def test_healthz_ne_renvoie_jamais_de_trace(client_sans_base: AsyncClient) -> None:
    reponse = await client_sans_base.get("/healthz")
    assert "Traceback" not in reponse.text
    # L'URL de connexion contient un mot de passe : elle ne doit jamais fuiter.
    assert "postgresql" not in reponse.text
