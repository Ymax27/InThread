"""Tests de `app/config.py` : validation de SECRET_KEY et lecture de l'environnement."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.config import SECRET_KEY_PAR_DEFAUT, Settings


def test_secret_key_par_defaut_refusee_en_production() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="production", secret_key=SECRET_KEY_PAR_DEFAUT)


def test_secret_key_vide_refusee_en_production() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="production", secret_key="   ")


def test_secret_key_valide_acceptee_en_production() -> None:
    reglages = Settings(
        app_env="production",
        secret_key="une-cle-longue-et-aleatoire-suffisante-pour-signer",
        allowed_hosts="example.cm,www.example.cm",
    )
    assert reglages.is_production
    assert reglages.hosts == ["example.cm", "www.example.cm"]


def test_secret_key_par_defaut_acceptee_en_developpement() -> None:
    assert not Settings(app_env="development").is_production


def test_allowed_hosts_avec_espaces() -> None:
    assert Settings(allowed_hosts=" localhost , 127.0.0.1 ,").hosts == [
        "localhost",
        "127.0.0.1",
    ]


def test_variables_momo_et_ia_sont_facultatives() -> None:
    # Les clés MoMo / IA n'existent pas en phase 1 : leurs défauts doivent passer.
    reglages = Settings(app_env="development")
    assert reglages.momo_api_key == ""
    assert reglages.ai_provider == "none"
    assert reglages.sandbox_interval_minutes == 60
