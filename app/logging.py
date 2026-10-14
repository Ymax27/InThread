"""Journalisation : texte en dev/test, JSON compact en production.

Les journaux ne contiennent jamais de secret : on ne journalise ni réglages,
ni mots de passe, ni jetons, ni en-tête `Authorization`.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime

from app.config import Settings


class JsonFormatter(logging.Formatter):
    """Format JSON une ligne par événement (facile à lire pour Datacloud)."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, str] = {
            "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(settings: Settings) -> None:
    """Configure la racine du logger. Idempotent (les tests recréeront l'app)."""
    handler = logging.StreamHandler(sys.stdout)
    if settings.is_production:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(levelname)-7s %(name)s: %(message)s"))

    root = logging.getLogger()
    root.handlers.clear()  # évite les doubles messages quand create_app est rappelé
    root.addHandler(handler)
    root.setLevel(settings.log_level.upper())
