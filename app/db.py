"""Moteur SQLAlchemy async, sessions et base déclarative.

Une seule instance de moteur par processus, créée à la première utilisation
(`init_db`) : `create_app` ne se connecte donc jamais à la base au démarrage.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

log = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base déclarative : les modèles (phase 2) héritent de cette classe."""


_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_db(url: str | None = None) -> None:
    """Crée le moteur et la fabrique de sessions (no-op s'ils existent déjà)."""
    global _engine, _session_factory
    if _engine is not None:
        return
    if url is None:
        from app.config import get_settings

        url = get_settings().database_url
    # pool_pre_ping : une requête « SELECT 1 » avant chaque emprunt de connexion,
    # cela évite les « server closed the connection » après une longue veille.
    _engine = create_async_engine(url, pool_pre_ping=True)
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Renvoie la fabrique de sessions en créant le moteur si besoin."""
    init_db()
    if _session_factory is None:  # pragma: no cover - défense en profondeur
        raise RuntimeError("Moteur de base de données non initialisé")
    return _session_factory


async def get_session() -> AsyncIterator[AsyncSession]:
    """Dépendance FastAPI : fournit une session par requête, fermée automatiquement."""
    async with get_session_factory()() as session:
        yield session


async def dispose_db() -> None:
    """Ferme le moteur (fin de test, arrêt propre). Le prochain appel le recrée."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None


async def database_reachable(delai: float) -> bool:
    """Vrai si `SELECT 1` répond dans `delai` secondes, faux sinon (jamais d'exception)."""
    try:
        async with asyncio.timeout(delai):
            async with get_session_factory()() as session:
                await session.execute(text("SELECT 1"))
        return True
    except TimeoutError:
        log.warning("Base de données injoignable : délai de %s s dépassé", delai)
        return False
    except Exception as exc:
        # On journalise le *type* d'erreur, jamais l'URL de connexion (elle contient
        # le mot de passe).
        log.warning("Base de données injoignable : %s", type(exc).__name__)
        return False
