"""Tests de la page d'accueil, des en-têtes de sécurité, du mode léger et du 404."""

from __future__ import annotations

import re

from httpx import AsyncClient


async def test_accueil_200_et_langue_francaise(client: AsyncClient) -> None:
    reponse = await client.get("/")
    assert reponse.status_code == 200
    assert reponse.headers["content-type"].startswith("text/html")
    assert 'lang="fr"' in reponse.text
    assert "recettes d'intégration africaines" in reponse.text.lower()


async def test_accueil_porte_les_entetes_de_securite(client: AsyncClient) -> None:
    reponse = await client.get("/")
    entetes = reponse.headers
    csp = entetes.get("content-security-policy", "")
    assert "default-src 'self'" in csp
    assert "script-src 'self'" in csp
    assert "frame-ancestors 'none'" in csp
    assert entetes["x-content-type-options"] == "nosniff"
    assert entetes["x-frame-options"] == "DENY"
    assert entetes["referrer-policy"] == "strict-origin-when-cross-origin"
    assert "camera=()" in entetes["permissions-policy"]
    # HSTS réservée à la production : en test, elle forcerait https:// inutilement.
    assert "strict-transport-security" not in entetes


async def test_accueil_sans_javascript_inline(client: AsyncClient) -> None:
    """La CSP interdit script/style inline : rien d'interdit ne doit fuiter dans le HTML."""
    html = (await client.get("/")).text
    assert not re.search(r"<script(?![^>]*\bsrc=)", html), "script inline détecté"
    assert "onclick=" not in html
    assert "hx-on" not in html
    assert not re.search(r'\sstyle="', html), "style inline détecté"
    # HTMX bien vendorisé, jamais appelé depuis un CDN.
    assert "/static/js/htmx.min.js" in html
    assert "http://cdn" not in html and "https://cdn" not in html


async def test_accueil_html_complet(client: AsyncClient) -> None:
    html = (await client.get("/")).text
    assert "<footer" in html
    assert "<header" in html


async def test_requete_htmx_renvoie_un_seul_fragment(client: AsyncClient) -> None:
    """Une requête HTMX ne reçoit que le fragment `<main>` : pas de double en-tête/pied."""
    html = (await client.get("/", headers={"HX-Request": "true"})).text
    assert "hero__titre" in html  # le contenu du `<main>` est bien là
    assert "<footer" not in html
    assert "<header" not in html
    assert len(html) < len((await client.get("/")).text)


async def test_requete_sans_htmx_renvoie_la_page_complete(client: AsyncClient) -> None:
    """Sans l'en-tête HX-Request (navigateur, curl, lecteur d'écran) : page complète."""
    html = (await client.get("/")).text
    assert "<footer" in html


async def test_mode_lite_via_requete(client: AsyncClient) -> None:
    reponse = await client.get("/?lite=1")
    assert reponse.status_code == 200
    assert 'data-lite="1"' in reponse.text
    # En mode léger : ni HTMX, ni motif décoratif.
    assert "/static/js/htmx.min.js" not in reponse.text
    assert "frieze" not in reponse.text
    assert "lite=1" in reponse.headers.get("set-cookie", "")


async def test_mode_lite_via_cookie(client: AsyncClient) -> None:
    await client.get("/?lite=1")
    reponse = await client.get("/")  # le cookie accompagne la requête suivante
    assert 'data-lite="1"' in reponse.text
    assert "/static/js/htmx.min.js" not in reponse.text


async def test_mode_lite_desactive(client: AsyncClient) -> None:
    reponse = await client.get("/?lite=0")
    assert 'data-lite="0"' in reponse.text
    assert "lite=1" not in reponse.headers.get("set-cookie", "")


async def test_mode_lite_via_en_tete_save_data(client: AsyncClient) -> None:
    reponse = await client.get("/", headers={"Save-Data": "on"})
    assert reponse.status_code == 200
    assert 'data-lite="1"' in reponse.text
    # L'en-tête n'active que la requête : on ne pose pas de cookie.
    assert "lite=1" not in reponse.headers.get("set-cookie", "")


async def test_404_en_html(client: AsyncClient) -> None:
    reponse = await client.get("/page-qui-nexiste-pas")
    assert reponse.status_code == 404
    assert reponse.headers["content-type"].startswith("text/html")
    assert "Page introuvable" in reponse.text
    assert 'lang="fr"' in reponse.text


async def test_recettes_renvoie_un_404_propre(client: AsyncClient) -> None:
    """La recherche pointe vers /recettes (phase 3) : 404 propre, pas d'erreur 500."""
    reponse = await client.get("/recettes", params={"q": "mtn momo"})
    assert reponse.status_code == 404
    assert "Page introuvable" in reponse.text


async def test_planche_design_disponible_hors_production(client: AsyncClient) -> None:
    reponse = await client.get("/_design")
    assert reponse.status_code == 200
    assert "Planche de design" in reponse.text
    assert "badge-works" in reponse.text
    assert "Fonctionne" in reponse.text


async def test_page_hors_ligne(client: AsyncClient) -> None:
    reponse = await client.get("/hors-ligne")
    assert reponse.status_code == 200
    assert "Hors ligne" in reponse.text


async def test_css_sert_avec_cache_long(client: AsyncClient) -> None:
    reponse = await client.get("/static/css/app.css")
    assert reponse.status_code == 200
    assert reponse.headers["content-type"].startswith("text/css")
    assert "max-age=604800" in reponse.headers["cache-control"]
    assert reponse.headers.get("content-security-policy")
