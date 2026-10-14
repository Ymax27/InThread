#!/usr/bin/env python3
"""Contrôle des licences des dépendances (règle non négociable du CADEV 2026).

- échoue (code 1) si une licence contient GPL / LGPL / AGPL ;
- signale en avertissement les licences « faiblement copyleft » (MPL, EPL, CDDL)
  et les licences inconnues : Max décide au cas par cas ;
- réécrit la table générée de `THIRD_PARTY_LICENSES.md` en conservant
  l'en-tête du fichier (il est protégé par un marqueur HTML).

Usage : `python scripts/check_licenses.py`
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
RAPPORT = RACINE / "THIRD_PARTY_LICENSES.md"

# Marqueur posé dans THIRD_PARTY_LICENSES.md : tout ce qui précède est conservé.
MARQUEUR = "<!-- La table générée par pip-licenses sera insérée ci-dessous par la CI. -->"

# Interdites par le règlement (une seule famille suffit à bloquer).
INTERDITES = ("GPL", "LGPL", "AGPL")

# Faiblement copyleft ou à confirmer : on n'échoue pas, on alerte Max.
SOUS_VIGILANCE = ("MPL", "EPL", "CDDL", "ECLIPSE", "EUPL", "UNKNOWN", "SEE LICENSE")


def _executable_pip_licenses() -> str:
    """Chemin de `pip-licenses` : à côté de l'interpréteur courant (venv), sinon PATH.

    On ne fait PAS `resolve()` : dans un venv, `python` est un lien symbolique vers
    l'interpréteur système, seule la version non résolue pointe dans le venv.
    """
    for dossier in (Path(sys.executable).parent, Path(sys.prefix) / "bin"):
        voisin = dossier / "pip-licenses"
        if voisin.exists():
            return str(voisin)
    return "pip-licenses"


def lire_inventaire() -> list[dict[str, str]]:
    """Interroge pip-licenses (JSON) et renvoie la liste des paquets installés."""
    try:
        resultat = subprocess.run(
            [_executable_pip_licenses(), "--format=json", "--with-urls"],
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        sys.exit("pip-licenses introuvable : installer requirements-dev.txt")
    except subprocess.CalledProcessError as exc:
        sys.exit(f"pip-licenses a échoué : {exc.stderr.strip()}")
    return json.loads(resultat.stdout)


def classifier(paquets: list[dict[str, str]]) -> tuple[list[str], list[str]]:
    """Sépare les licences interdites (bloquantes) des licences à surveiller."""
    interdites: list[str] = []
    vigilance: list[str] = []
    for paquet in sorted(paquets, key=lambda p: p["Name"].lower()):
        licence = paquet.get("License", "").strip() or "UNKNOWN"
        nom = f"{paquet['Name']} {paquet['Version']} — {licence}"
        if any(mot in licence.upper() for mot in INTERDITES):
            interdites.append(nom)
        elif any(mot in licence.upper() for mot in SOUS_VIGILANCE):
            vigilance.append(nom)
    return interdites, vigilance


def table_markdown(paquets: list[dict[str, str]]) -> str:
    """Table Markdown triée, à insérer sous le marqueur."""
    lignes = [
        "| Composant | Version | Licence | URL |",
        "|---|---|---|---|",
    ]
    for paquet in sorted(paquets, key=lambda p: p["Name"].lower()):
        url = paquet.get("URL", "").replace("|", "\\|") or "—"
        licence = (paquet.get("License", "").strip() or "UNKNOWN").replace("|", "\\|")
        lignes.append(f"| {paquet['Name']} | {paquet['Version']} | {licence} | {url} |")
    return "\n".join(lignes)


def ecrire_rapport(paquets: list[dict[str, str]]) -> None:
    """Réécrit la table du rapport, en gardant strictement tout l'en-tête."""
    contenu = RAPPORT.read_text(encoding="utf-8")
    if MARQUEUR not in contenu:
        sys.exit(f"Marqueur introuvable dans {RAPPORT.name} : refus d'écraser l'en-tête.")
    entete, _ancienne_table = contenu.split(MARQUEUR, 1)
    RAPPORT.write_text(f"{entete}{MARQUEUR}\n\n{table_markdown(paquets)}\n", encoding="utf-8")


def main() -> int:
    paquets = lire_inventaire()
    interdites, vigilance = classifier(paquets)

    print(f"{len(paquets)} paquets analysés.")
    ecrire_rapport(paquets)
    print(f"Table écrite dans {RAPPORT.relative_to(RACINE)}")

    for nom in vigilance:
        print(f"ATTENTION — licence à valider par l'équipe : {nom}")
    for nom in interdites:
        print(f"INTERDIT — licence non permissive : {nom}")

    if interdites:
        print(f"\n{len(interdites)} dépendance(s) incompatible(s) avec le règlement CADEV.")
        return 1

    if vigilance:
        print(f"\n{len(vigilance)} licence(s) en vigilance : décision de Max requise.")
    else:
        print("\nAucune licence bloquante.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
