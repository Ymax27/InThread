"""Crée les extensions de recherche : pg_trgm, unaccent, et vector (optionnelle).

Revision ID: 0001_extensions
Revises:
Create Date: 2026-10-12

`pg_trgm` et `unaccent` sont indispensables (recherche floue et française).
`vector` (pgvector) est optionnelle : si elle est absente, les embeddings seront
stockés en JSON et comparés en Python (§5). Son échec est donc isolé dans une
sauvegarde de transaction (SAVEPOINT) : sans cela, l'erreur aborterait toute la
migration.
"""

from __future__ import annotations

import logging

import sqlalchemy as sa
from alembic import op

revision = "0001_extensions"
down_revision = None
branch_labels = None
depends_on = None

log = logging.getLogger(__name__)


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
    conn.execute(sa.text("CREATE EXTENSION IF NOT EXISTS unaccent"))

    try:
        with conn.begin_nested():  # SAVEPOINT : échec isolé, la transaction reste valide
            conn.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))
    except Exception as exc:  # noqa: BLE001 - on relit juste le motif d'échec
        log.warning(
            "Extension vector indisponible (%s) : les embeddings seront stockés en JSON.",
            type(exc).__name__,
        )


def downgrade() -> None:
    conn = op.get_bind()
    # On ne retire `vector` que si on l'a créée : DROP silencieux si absente.
    for extension in ("vector", "unaccent", "pg_trgm"):
        try:
            with conn.begin_nested():
                conn.execute(sa.text(f"DROP EXTENSION IF EXISTS {extension}"))
        except Exception as exc:  # noqa: BLE001
            log.warning("Impossible de supprimer %s (%s)", extension, type(exc).__name__)
