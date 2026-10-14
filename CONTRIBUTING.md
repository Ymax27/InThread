# Contribuer à {{NOM_PROJET}}

Merci ! Ce projet est développé pendant **CADEV 2026** : toute contribution doit être **originale** (écrite pendant le concours) et sous **licence permissive**.

## Règles d'or

1. **Aucune dépendance GPL, LGPL ou AGPL.** Avant d'ajouter une dépendance, vérifier sa licence (et celles de ses dépendances). La CI bloque sinon.
2. **Aucun secret dans le code** : clés MoMo, clés IA, `SECRET_KEY` vont dans `.env` (local) ou dans les secrets GitHub / Datacloud.
3. **Pas de copie de code** d'un projet existant (y compris nos anciens projets).
4. **Déclarer l'usage de l'IA** dans [AI_USAGE.md](AI_USAGE.md) et dans la description de la PR.
5. **Comprendre ce qu'on fusionne** : si du code a été généré, quelqu'un de l'équipe doit pouvoir l'expliquer.

## Flux de travail

- Branche à partir de `main` : `feat/…`, `fix/…`, `docs/…`, `recette/…`.
- Commits courts et explicites, en français ou en anglais (`feat: page /statut`, `fix: calcul de l'état`).
- Ouvrir une pull request avec le modèle fourni ; la CI doit être verte avant fusion.
- `main` est déployée automatiquement sur Datacloud : ne jamais y pousser du code non testé.

## Avant d'ouvrir une PR

```bash
docker compose --profile dev run --rm dev ruff check .
docker compose --profile dev run --rm dev ruff format --check .
docker compose --profile dev run --rm dev pytest
```

(Équivalent sans Docker, avec un venv local : `pip install -r requirements-dev.txt`, puis les mêmes commandes sans `docker compose`.)

## Proposer une recette

Utiliser le modèle [docs/RECETTE_TEMPLATE.md](docs/RECETTE_TEMPLATE.md), ou ouvrir une issue « Nouvelle recette ». Une recette doit avoir été **testée réellement** par son auteur, et ne contenir **aucune vraie clé, aucun vrai numéro de client**.

## Signaler un bug

Ouvrir une issue avec le modèle « Bug ». Pour une faille de sécurité, ne pas ouvrir d'issue publique : contacter le capitaine ({{CONTACT_SECURITE}}).
