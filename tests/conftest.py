"""Configuration des tests.

Les variables d'environnement sont posées AVANT le premier import de `app.*` :
les réglages sont mis en cache (`lru_cache`), il faut donc fixer l'environnement
avant toute lecture.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest

os.environ.setdefault("APP_ENV", "test")
# Clé de test uniquement : jamais utilisée en production (Settings refuse la valeur par défaut).
os.environ.setdefault("SECRET_KEY", "secret-de-test-suffisant-pour-les-tests-000000000")
# Le client de test httpx envoie Host: testserver.
os.environ.setdefault("ALLOWED_HOSTS", "testserver,localhost,127.0.0.1")
# PostgreSQL réel obligatoire (service CI ou cluster local), jamais SQLite :
# les types et l'étendue asyncpg ne sont pas interchangeable.
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://app:app@127.0.0.1:5432/app")

from httpx import ASGITransport, AsyncClient  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.db import dispose_db  # noqa: E402


@pytest.fixture(autouse=True)
async def _isoler_reglages() -> AsyncIterator[None]:
    """Recharge les réglages avant/après chaque test et ferme le moteur de DB."""
    get_settings.cache_clear()
    await dispose_db()
    yield
    get_settings.cache_clear()
    await dispose_db()


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """Client HTTP branché sur l'application réelle (sans cycle de vie ASGI)."""
    from app.main import create_app

    transport = ASGITransport(app=create_app())
    async with AsyncClient(transport=transport, base_url="http://testserver") as http:
        yield http


@pytest.fixture
async def client_sans_base(monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[AsyncClient]:
    """Client dont la base est injoignable (port fermé) : /healthz doit renvoyer 503."""
    from app.config import get_settings as _get_settings
    from app.main import create_app

    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://app:wrong@127.0.0.1:1/app")
    _get_settings.cache_clear()
    await dispose_db()

    transport = ASGITransport(app=create_app())
    async with AsyncClient(transport=transport, base_url="http://testserver") as http:
        yield http
