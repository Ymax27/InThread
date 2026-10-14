#!/usr/bin/env python3
"""Mesure le poids réellement transféré d'une page (budget : 50 Ko).

Récupère la page, puis chaque CSS et JS qu'elle référence, avec
`Accept-Encoding: gzip` : on mesure donc les octets **compressés** envoyés au
navigateur, exactement ce que compte le budget du concours.

Usage : `python scripts/page_budget.py http://localhost:8000/ [--budget 50]`
Les pages d'exclusion (planche de design interne) ne sont jamais mesurées.
"""

from __future__ import annotations

import argparse
import gzip
import re
import urllib.error
import urllib.request
from urllib.parse import urljoin, urlparse

# Poids maximal, en Ko, compressé, pour une page entière.
BUDGET_PAR_DEFAUT = 50

# Pages jamais mesurées (interne / hors produit).
EXCLUSIONS = ("/_design",)

UA = "page-budget/1.0 (CADEV 2026)"

RE_CSS = re.compile(r'<link[^>]+rel="stylesheet"[^>]+href="([^"]+)"')
RE_JS = re.compile(r'<script[^>]+src="([^"]+)"')


def telecharger(url: str) -> tuple[int, bytes]:
    """Renvoie (taille compressée, contenu décompressé) d'une ressource."""
    # L'URL vient du HTML de la page : on refuse tout autre schéma que http(s).
    if urlparse(url).scheme not in ("http", "https"):
        raise ValueError(f"schéma refusé : {urlparse(url).scheme!r}")
    # noqa ci-dessous : schéma http(s) vérifié juste avant, URL d'origine = HTML servi par notre propre app.
    requete = urllib.request.Request(  # noqa: S310
        url, headers={"Accept-Encoding": "gzip", "User-Agent": UA}
    )
    with urllib.request.urlopen(requete, timeout=15) as reponse:  # noqa: S310 — schéma vérifié au-dessus
        corps = reponse.read()  # urllib ne décompresse pas : c'est le poids réseau
        encodage = (reponse.headers.get("Content-Encoding") or "").lower()
    if encodage == "gzip":
        return len(corps), gzip.decompress(corps)
    return len(corps), corps


def ressources_referencees(html: str, base: str) -> list[str]:
    """URLs (absolues) des feuilles de styles et scripts référencés par la page."""
    hrefs = RE_CSS.findall(html) + RE_JS.findall(html)
    urls = [urljoin(base, href) for href in hrefs]
    # Seules les ressources du même hôte sont comptées (pas de CDN tiers ici).
    hote = urlparse(base).netloc
    return [u for u in urls if urlparse(u).netloc in ("", hote)]


def mesurer(page: str, budget_ko: int) -> int:
    """Affiche le détail par ressource et renvoie le code de sortie."""
    try:
        taille_html, contenu_html = telecharger(page)
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        print(f"Impossible de récupérer {page} : {exc}")
        return 1

    html = contenu_html.decode("utf-8", errors="replace")
    detail: list[tuple[str, int]] = [(page, taille_html)]

    for url in ressources_referencees(html, page):
        chemin = urlparse(url).path
        if any(chemin.startswith(exclu) for exclu in EXCLUSIONS):
            continue
        try:
            taille, _contenu = telecharger(url)
        except (urllib.error.URLError, TimeoutError) as exc:
            print(f"Ressource introuvable ({url}) : {exc}")
            return 1
        detail.append((url, taille))

    total = sum(taille for _, taille in detail)
    budget = budget_ko * 1024

    print(f"Page : {page}")
    for url, taille in detail:
        print(f"  {taille:>7} o  {url}")
    print(f"  {'=' * 7}  TOTAL {total} o / {budget} o ({total / 1024:.1f} Ko)")

    if total > budget:
        print(f"DÉPASSEMENT : {total - budget} o au-dessus du budget de {budget_ko} Ko.")
        return 1
    print(f"OK : {budget - total} o de marge.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Budget de poids d'une page (50 Ko).")
    parser.add_argument("url", help="URL complète de la page à mesurer")
    parser.add_argument(
        "--budget", type=int, default=BUDGET_PAR_DEFAUT, help="budget en Ko (défaut 50)"
    )
    args = parser.parse_args(argv)
    return mesurer(args.url, args.budget)


if __name__ == "__main__":
    raise SystemExit(main())
