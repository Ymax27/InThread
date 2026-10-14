## Ce que fait cette PR
<!-- Résumé en 2-3 phrases. Lier l'issue : Closes #… -->

## Type
- [ ] Fonctionnalité
- [ ] Correction
- [ ] Contenu (recette)
- [ ] Documentation
- [ ] Infra / CI

## Comment tester
```bash
# commandes à lancer
```

## Captures (si UI)
<!-- mobile + desktop ; idéalement mode léger et sans JS -->

## Usage de l'IA
- [ ] Aucun
- [ ] Assisté par IA (outil : …)
- [ ] Généré par IA puis relu (outil : … ; fichiers : …)

Relu et compris par : @…  — [AI_USAGE.md](../AI_USAGE.md) mis à jour : [ ] oui

## Checklist
- [ ] `ruff check` et `ruff format --check` passent
- [ ] `pytest` passe ; tests ajoutés pour la logique nouvelle
- [ ] Aucune nouvelle dépendance, **ou** licence vérifiée (pas de GPL / LGPL / AGPL) et ajoutée au README
- [ ] Aucun secret, aucune clé, aucun `.env` commité
- [ ] Les pages touchées restent < 50 Ko et fonctionnent sans JS
- [ ] Accessibilité vérifiée (labels, contraste, clavier)
- [ ] Migrations Alembic incluses si le modèle change
