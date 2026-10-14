"""Pages HTML de la phase 1 : accueil, planche de design, page hors ligne.

La base de données n'est pas encore utilisée : les recettes et l'aperçu sandbox
sont codés en dur et clairement marqués comme exemples / aperçu.
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from starlette.responses import HTMLResponse

from app.templating import render

# Routeur des pages toujours disponibles.
router = APIRouter()
# Routeur de la planche de design : jamais montée en production (voir main.py).
design_router = APIRouter()

# --- Aperçu de la page /statut (données factices, vraies données en phase 5) ---
APERCU_SANDBOX = {
    "derniere_execution": "il y a 14 min",
    "succes_24h": "96 %",
    "succes_7j": "93 %",
    "latence_moyenne": "412 ms",
    "derniere_erreur": "aucune (données factices)",
}

# --- Recettes d'exemple : la table `recipes` arrive en phase 2 ---
# `exemple: True` fait afficher le badge « Exemple » sur la carte.
RECETTES_EXEMPLE = [
    {
        "slug": "momo-collection-python-httpx",
        "exemple": True,
        "title": "Encaisser un paiement MTN MoMo (Collection) avec Python",
        "provider": "mtn_momo",
        "provider_label": "MTN MoMo",
        "country_label": "Cameroun",
        "stack": "Python 3.12 + httpx",
        "status": "works",
        "problem": "Envoyer une demande de paiement et connaître son statut final.",
    },
    {
        "slug": "orange-money-web-payment-php",
        "exemple": True,
        "title": "Initier un paiement Orange Money web (Web Payment) en PHP",
        "provider": "orange_money",
        "provider_label": "Orange Money",
        "country_label": "Côte d'Ivoire",
        "stack": "PHP 8.3 + cURL",
        "status": "unverified",
        "problem": "Rediriger un client vers la page de paiement puis vérifier la transaction.",
    },
    {
        "slug": "wave-checkout-node",
        "exemple": True,
        "title": "Créer une session de paiement Wave Checkout (Sénégal)",
        "provider": "wave",
        "provider_label": "Wave",
        "country_label": "Sénégal",
        "stack": "Node.js 20",
        "status": "works",
        "problem": "Ouvrir une session de paiement et recevoir le webhook de confirmation.",
    },
]


@router.get("/", response_class=HTMLResponse)
async def accueil(request: Request) -> HTMLResponse:
    """Page d'accueil : héros, recherche, étapes, aperçu sandbox, exemples."""
    return render(
        request,
        "pages/home.html",
        {
            "apercu_sandbox": APERCU_SANDBOX,
            "recettes_exemple": RECETTES_EXEMPLE,
        },
        partial="partials/home_main.html",
    )


@router.get("/hors-ligne", response_class=HTMLResponse)
async def hors_ligne(request: Request) -> HTMLResponse:
    """Page affichée par le service worker (phase 7) quand il n'y a pas de réseau."""
    return render(request, "pages/offline.html", status_code=200)


@design_router.get("/_design", response_class=HTMLResponse)
async def planche_design(request: Request) -> HTMLResponse:
    """Planche de design : tous les composants du système, pour valider le style."""
    return render(
        request,
        "pages/design.html",
        {"recettes_exemple": RECETTES_EXEMPLE},
        partial="partials/design_main.html",
    )
