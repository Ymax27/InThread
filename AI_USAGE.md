# Journal d'usage de l'IA

Le règlement CADEV 2026 autorise l'IA à condition de **déclarer les outils utilisés et les parties concernées**. Ce journal est tenu **au fil du projet** : une ligne par session ou par pull request significative. Le jury peut interroger l'équipe sur n'importe quelle partie, y compris celles générées par l'IA : chaque entrée doit donc indiquer qui a relu et compris le code.

## Outils déclarés

| Outil | Éditeur | Usage principal | Depuis |
|---|---|---|---|
| Freebuff | TODO | Agent de code : génération et modification de code dans le dépôt | 2026-10-12 |
| Grok Bot | — | Cadrage, architecture, planning, rédaction de documentation | 2026-10-11 |
| TODO (API IA du produit) | TODO | Embeddings (doublons) et adaptation de stack, **dans le produit** | TODO |

## Niveaux d'intervention

- **G** — Généré par l'IA, puis relu et testé par un membre de l'équipe.
- **A** — Écrit par l'équipe avec assistance de l'IA (suggestions, corrections, explications).
- **M** — Écrit à la main, sans IA.

## Journal

| Date | Outil | Phase / PR | Fichiers ou parties | Niveau | Relu et compris par | Tests | Remarques (ce qui a été modifié à la main, choix expliqués) |
|---|---|---|---|---|---|---|---|
| 2026-10-11 | Grok Bot | Cadrage | README.md, docs, modèles de dépôt | A | Lindsell Maxwell | — | Documentation initiale du dépôt |
| 2026-10-12 | Freebuff | Phase 1 | app/ (config, db, main, lite, templating, routes, security/headers), worker/, migrations/, tests/, scripts/, Dockerfile, docker-compose.yml, .github/workflows/ci.yml | G | TODO (à répartir dans l'équipe) | 24 tests pytest verts + ruff + budget de 50 Ko vérifié | Choix arrêtés à la main avant génération : nom « MboaRec », palette kola, absence totale de JS inline (`onclick`, `hx-on`) imposée par la CSP stricte, en-tête `HX-Request` comme seul signal de fragment, `python:3.12-slim` non-root pour l'image |
| | | | | | | | |

## Prompts importants

Conserver ici (ou dans `docs/prompts/`) les prompts significatifs envoyés à Freebuff, pour pouvoir montrer au jury comment l'IA a été dirigée.

| Date | Phase | Fichier du prompt |
|---|---|---|
| 2026-10-12 | Phase 1 | [FREEBUFF_PROMPT.md](FREEBUFF_PROMPT.md) |

## Points de maîtrise à préparer pour le jury

Pour chaque partie générée, être capable d'expliquer :

- [ ] La fabrique d'application FastAPI et l'injection de la session de base de données
- [ ] Les migrations Alembic en mode async
- [ ] Le fonctionnement des sessions par cookie signé et du jeton CSRF
- [ ] Le hachage Argon2id et le verrouillage après échecs
- [ ] La règle d'état des recettes (`recipe_status.py`) et ses tests
- [ ] Le parcours sandbox MoMo (token → requesttopay → statut) et la gestion des erreurs
- [ ] Le service worker (stratégies de cache) et la page hors ligne
- [ ] La couche `ai_provider` et le repli sans IA
- [ ] Le contrôle des licences et le budget de poids en CI
