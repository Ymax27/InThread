"""Réglages de l'application.

Toutes les valeurs viennent de l'environnement (ou du fichier local `.env`,
jamais commité). Les noms de variables sont ceux de `.env.example`.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Valeur de démonstration : interdite en production (voir _secret_key_valide).
SECRET_KEY_PAR_DEFAUT = "change-me"  # noqa: S105 — ce n'est PAS un secret, c'est le leurre refusé par le validateur.

# Liste des hôtes acceptés par TrustedHostMiddleware (voir app/main.py).
_SEPARATEUR_HOSTS = ","


class Settings(BaseSettings):
    """Réglages de l'application, lus depuis l'environnement."""

    # `extra="ignore"` : des variables comme POSTGRES_USER coexistent dans le même .env.
    # `env_ignore_empty=True` : une variable vide (ex. MOMO_API_KEY=) ne vaut pas la peine
    # d'écraser la valeur par défaut.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_ignore_empty=True,
    )

    # --- Application ---
    app_env: Literal["development", "test", "production"] = "development"
    secret_key: str = SECRET_KEY_PAR_DEFAUT
    project_name: str = "MboaRec"
    base_url: str = "http://localhost:8000"
    allowed_hosts: str = "localhost,127.0.0.1"
    session_cookie_secure: bool = False
    log_level: str = "INFO"

    # --- Base de données (pilote asyncpg) ---
    database_url: str = "postgresql+asyncpg://app:app@db:5432/app"
    # Délai maximal du `SELECT 1` de /healthz, en secondes.
    db_timeout_seconds: float = 2.0
    # Utilisés par docker compose pour démarrer le conteneur `db`, pas par l'app.
    postgres_user: str = "app"
    # Mot de passe du conteneur de développement docker compose, jamais en production.
    postgres_password: str = "app"  # noqa: S105
    postgres_db: str = "app"

    # --- MTN MoMo sandbox (utilisé à partir de la phase 4) ---
    momo_base_url: str = "https://sandbox.momodeveloper.mtn.com"
    momo_target_env: str = "sandbox"
    momo_collection_subscription_key: str = ""
    momo_api_user: str = ""
    momo_api_key: str = ""
    momo_currency: str = "EUR"
    momo_test_msisdn: str = "46733123455"
    sandbox_interval_minutes: int = 60

    # --- IA (phases 8 et 9) : `none` = IA désactivée ---
    ai_provider: str = "none"
    ai_api_key: str = ""
    ai_base_url: str = ""
    ai_embedding_model: str = ""
    ai_chat_model: str = ""
    ai_timeout_seconds: int = 15

    # --- Limitation de débit (slowapi, phase 2) ---
    rate_limit_storage_uri: str = "memory://"

    @property
    def is_production(self) -> bool:
        """Vrai seulement pour APP_ENV=production (docs OpenAPI coupées, HSTS activé)."""
        return self.app_env == "production"

    @property
    def hosts(self) -> list[str]:
        """ALLOWED_HOSTS lisible : « localhost,127.0.0.1 » -> ["localhost", "127.0.0.1"]."""
        return [h.strip() for h in self.allowed_hosts.split(_SEPARATEUR_HOSTS) if h.strip()]

    @model_validator(mode="after")
    def _secret_key_valide(self) -> Settings:
        """Refuse de démarrer en production avec la clé de démonstration (règle de sécurité §7)."""
        if self.is_production and self.secret_key.strip() in ("", SECRET_KEY_PAR_DEFAUT):
            raise ValueError(
                "SECRET_KEY obligatoire et différente de la valeur par défaut en production."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    """Instance unique des réglages (mise en cache).

    `get_settings.cache_clear()` permet aux tests de relire l'environnement.
    """
    return Settings()
