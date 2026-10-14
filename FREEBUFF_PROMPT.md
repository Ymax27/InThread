# Prompt Freebuff — {{NOM_PROJET}} (CADEV 2026)

> **Mode d'emploi pour Max :** colle tout le bloc « PROMPT PHASE 1 » ci-dessous dans Freebuff, ouvert à la racine du dépôt. Quand la phase 1 est terminée, relue et commitée, colle le bloc « PROMPT PHASE 2 » (en bas). Garde chaque prompt envoyé dans `AI_USAGE.md` (journal), c'est exigé par le règlement.
> Remplace `{{NOM_PROJET}}` quand le nom sera choisi (un rechercher/remplacer suffit).

---

## PROMPT PHASE 1

Tu es l'ingénieur principal (backend + frontend) d'une équipe qui participe à **CADEV 2026**, un concours de développement en ligne organisé par Systalink pour l'Afrique francophone. Tu travailles **dans ce dépôt Git**, avec Max (Lindsell Maxwell, capitaine, développeur et designer, Yaoundé). Max doit pouvoir **expliquer chaque ligne au jury** : tu écris un code simple, lisible, commenté là où c'est non trivial, et tu expliques tes choix.

Lis d'abord `README.md`, `CONTRIBUTING.md`, `docs/RECETTE_TEMPLATE.md` et `.env.example` : ils décrivent le produit et sont la référence. Ne les réécris pas ; mets-les à jour seulement si ton code change quelque chose qu'ils décrivent (et signale-le).

### 1. Le produit

Thème du concours : *« Construire la plateforme d'échange africaine, pour les devs, par les devs. Livrez un projet utilisable et hébergé en ligne. »*

**{{NOM_PROJET}}** est une plateforme de **recettes d'intégration africaines vérifiées** : des guides courts et testés, avec du code, pour intégrer MTN MoMo, Orange Money, Wave, SMS, USSD, etc. Chaque recette a : fournisseur, pays (ISO2), stack de base, problème, étapes, code, pièges.

- **Recettes MTN MoMo testées automatiquement** : un worker exécute toutes les heures le parcours de l'API **Collection** de la sandbox MTN (token → `requesttopay` avec un numéro de test documenté → lecture du statut). Chaque exécution est stockée (`sandbox_runs`). Badge « Vérifié automatiquement il y a X h ». Page publique `/statut` : dernière exécution, taux de succès 24 h / 7 j, latence, dernière erreur.
- **Vérification communautaire** pour les autres fournisseurs : boutons « Fonctionne encore » / « Cassée » avec une note.
- **Règle d'état** : si recette auto-testée et dernière exécution sandbox en échec → « Cassée (auto) » ; sinon « Cassée » si ≥ 2 signalements après la dernière confirmation ; sinon « Fonctionne » si une confirmation a moins de 90 jours ; sinon « À re-vérifier ».
- **Q&R sous chaque recette** (pas de forum séparé) : questions, réponses, votes +1/−1 (un par utilisateur et par contenu), réponse acceptée. **Réputation minimale** (un compteur) et **classement des contributeurs** filtrable par pays.
- **IA limitée à deux usages** : détection de doublons (embeddings, repli sur `pg_trgm` + plein texte) et bouton « Adapter à ma stack » (Django / Node / PHP), mis en cache, marqué « Adaptation IA, non vérifiée par la sandbox ». Via une couche `ai_provider` interchangeable sur httpx.
- **Connexion faible** : chaque page < **50 Ko transférés**, **fonctionne sans JavaScript**, PWA hors ligne (service worker écrit à la main, manifest, page hors ligne), **mode léger** (`?lite=1` + cookie, ou automatique si en-tête `Save-Data`).
- **Hors périmètre** (feuille de route seulement, ne pas coder) : WhatsApp, SMS, USSD comme canaux, sandboxes d'autres opérateurs, connexion GitHub, notifications, anglais, API publique.

### 2. Règles non négociables du concours

1. **Licences permissives uniquement** (MIT, BSD, Apache-2.0, ISC, PSF, 0BSD, PostgreSQL License). **Toute dépendance GPL, LGPL ou AGPL rend le projet inadmissible.** Donc : **pas de Django, pas de psycopg2, pas de psycopg 3** (LGPL). Le pilote PostgreSQL est **asyncpg**.
   - **Avant d'ajouter une dépendance**, quelle qu'elle soit (Python, JS, image Docker, police, icônes) : vérifie sa licence **et** celles de ses dépendances transitives notables, puis annonce-la dans ton résumé (`nom — version — licence — pourquoi`). Si tu as un doute, **n'ajoute pas** et demande à Max.
   - Préfère toujours la bibliothèque standard ou quelques lignes de code à une nouvelle dépendance.
   - Signale explicitement toute licence « faiblement copyleft » (ex. MPL-2.0, comme `certifi`) au lieu de l'ignorer : Max décidera avec l'équipe.
2. **Code original** écrit pendant le concours. Ne copie aucun code d'un projet existant (en particulier pas de l'ancien projet Django « DevHub Cameroun » de Max). Pas de copier-coller de gros extraits de tutoriels.
3. **Explicabilité** : l'usage de l'IA est déclaré, et le jury évalue la **maîtrise par l'équipe** du code généré. Pas de magie, pas d'abstraction inutile, pas de métaprogrammation. Une fonction = une responsabilité claire.
4. **Secrets** : uniquement dans l'environnement (`.env` local non commité, secrets GitHub / Datacloud). Jamais dans le code, les templates, les tests, les journaux ou le navigateur. Mets à jour `.env.example` (noms + valeurs factices) quand tu ajoutes une variable.
5. **Déploiement** : Systalink Datacloud (offre pas encore choisie). Rends l'app déployable comme simples conteneurs Docker configurés par variables d'environnement, sans dépendance à un fournisseur cloud précis.

### 3. Stack exacte

| Couche | Choix |
|---|---|
| Langage | Python 3.12 |
| Web | FastAPI + Uvicorn (Starlette en dessous) |
| Config | pydantic-settings (lecture de l'environnement) |
| ORM / migrations | SQLAlchemy 2.x **async** + Alembic (env.py async) |
| Pilote DB | asyncpg (`postgresql+asyncpg://…`) |
| Base | PostgreSQL 16 ; extensions `pg_trgm`, `unaccent` ; `vector` (pgvector) **optionnelle** (si absente : embeddings en JSON + cosinus en Python) |
| Templates | Jinja2 (rendu serveur), fragments HTMX dans `templates/partials/` |
| Interactions | HTMX (fichier `htmx.min.js` **vendorisé** dans `static/`, version épinglée, pas de CDN) |
| CSS | Tailwind CSS via le **CLI autonome** (binaire téléchargé par `scripts/get_tailwind.sh`, version épinglée, non versionné) — **pas de npm** dans le projet |
| Contenu | markdown-it-py + nh3 (assainissement) + Pygments (coloration côté serveur) |
| Auth | cookies de session signés (itsdangerous), mots de passe pwdlib + argon2-cffi (Argon2id), CSRF maison par jeton |
| Limitation de débit | slowapi |
| Worker | APScheduler dans un conteneur `worker` séparé (même image) |
| HTTP sortant | httpx (MoMo, IA) |
| Tests | pytest, pytest-asyncio, httpx `AsyncClient` / `ASGITransport`, Playwright (Python) pour quelques e2e |
| Qualité | ruff (lint + format) |
| Licences | pip-licenses + script `scripts/check_licenses.py` |
| Conteneurs | Dockerfile multi-étapes + docker compose (`app`, `worker`, `db`) |
| CI/CD | GitHub Actions |

Gestion des dépendances : `pyproject.toml` (métadonnées, config ruff/pytest) + `requirements.txt` et `requirements-dev.txt` **avec versions épinglées**.

### 4. Architecture et arborescence cible

```
app/
  __init__.py
  main.py              # create_app() : fabrique ; montage static, routeurs, middlewares, gestion d'erreurs
  config.py            # class Settings(BaseSettings) + get_settings() mis en cache
  db.py                # create_async_engine, async_sessionmaker, dépendance get_session()
  logging.py           # config de logs (JSON simple en prod), sans secrets
  models/              # modèles SQLAlchemy 2 (Mapped[], mapped_column) — phase 2
  schemas/             # Pydantic (formulaires, validation)
  services/            # logique métier pure, testable sans HTTP (recipe_status.py, reputation.py, search.py…)
  routes/              # pages.py, health.py, puis recipes.py, auth.py, status.py…
  security/            # sessions.py, passwords.py, csrf.py, headers.py, rate_limit.py
  ai/                  # provider.py (interface), none.py, http_provider.py — phase 6
  sandbox/             # momo.py (client Collection) — phase 4
  templates/
    base.html          # layout
    partials/          # fragments HTMX et composants (badge, card, flash, pagination)
    pages/             # home.html, offline.html, errors/404.html, errors/500.html
  static/
    src/app.css        # source Tailwind (@theme : tokens du design system)
    css/app.css        # généré, non versionné
    js/htmx.min.js     # vendorisé
    sw.js              # service worker — phase 7 (en phase 1 : rien, ou un fichier vide non enregistré)
    manifest.webmanifest
    icons/             # SVG/PNG légers
worker/
  __init__.py
  main.py              # démarre APScheduler ; en phase 1 : job « heartbeat » qui journalise seulement
migrations/            # Alembic (async)
tests/
  conftest.py
  test_health.py
  test_home.py
  e2e/                 # Playwright (phase 3+)
scripts/
  get_tailwind.sh
  check_licenses.py
  page_budget.py
docs/
Dockerfile
docker-compose.yml
alembic.ini
pyproject.toml
requirements.txt
requirements-dev.txt
.github/workflows/ci.yml
```

Principes : routes fines → services (logique) → modèles. La logique métier (règle d'état, réputation) est en **fonctions pures** testées unitairement. Toutes les dépendances (session DB, settings, utilisateur courant) passent par `Depends`. Pas de variable globale mutable.

### 5. Modèle de données (pour info, codé en phase 2)

- `users` : id, username (unique), email (unique, minuscule), password_hash, country (ISO2), reputation (int, défaut 0), failed_logins, locked_until, is_admin, created_at.
- `recipes` : id, author_id→users, slug (unique), title, provider (enum : mtn_momo, orange_money, wave, sms, ussd, autre), country, stack, problem_md, steps_md, code_md, pitfalls_md, (versions HTML rendues + assainies en cache), status (enum : works, broken, broken_auto, unverified), auto_tested (bool), last_verified_at, works_count, broken_count, search_vector (tsvector, GIN), embedding (nullable), created_at, updated_at. Index (provider, country, status), trigram sur title.
- `recipe_checks` : id, recipe_id, user_id, result (works/broken), note, api_version_or_env, created_at. Une vérification active par (recipe_id, user_id) : la plus récente compte.
- `sandbox_runs` : id, provider, started_at, success, failed_step (token/requesttopay/status, nullable), latency_ms, http_status, error_message (assaini, tronqué).
- `questions` : id, recipe_id (**obligatoire**), author_id, title, body_md, body_html, score, accepted_answer_id (nullable), search_vector, embedding (nullable), created_at, updated_at.
- `answers` : id, question_id, author_id, body_md, body_html, score, created_at, updated_at.
- `votes` : id, user_id, target_type (question/answer), target_id, value (−1/+1), created_at ; UNIQUE(user_id, target_type, target_id).
- `recipe_adaptations` : id, recipe_id, target_stack (django/node/php), content_md, model, source_hash, created_at ; UNIQUE(recipe_id, target_stack, source_hash).

### 6. Standards de code

- Typage partout (annotations), `from __future__ import annotations` si utile. ruff avec règles `E,F,I,B,UP,S,ASYNC` (S = sécurité/bandit), longueur de ligne 100.
- Identifiants (variables, fonctions, tables) **en anglais** ; **textes d'interface en français** ; commentaires et docstrings en **français**, courts, qui expliquent le *pourquoi*.
- Fonctions courtes ; pas de classe là où une fonction suffit.
- Erreurs : pages 404/500 propres en HTML, JSON seulement pour `/healthz`. Jamais de trace d'exception exposée en production.
- Tests : chaque comportement important a un test ; tests rapides ; base PostgreSQL réelle en CI (service Docker), transaction annulée par test.
- Commits atomiques avec message clair (`feat:`, `fix:`, `chore:`, `test:`, `docs:`). Ne pousse rien sur un dépôt distant : Max s'en charge.

### 7. Exigences de sécurité (dès la phase 1 quand c'est applicable)

- En-têtes sur toutes les réponses : `Content-Security-Policy` stricte (`default-src 'self'`; **aucun script ni style inline**, donc pas d'attributs `onclick`, pas de `<script>` inline, pas de `hx-on`), `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy` minimale, `X-Frame-Options: DENY`, HSTS seulement si `APP_ENV=production`.
- Configure HTMX pour respecter la CSP : `htmx.config.allowEval=false`, `includeIndicatorStyles=false` via `<meta name="htmx-config">`.
- `TrustedHostMiddleware` alimenté par `ALLOWED_HOSTS`. Documentation OpenAPI (`/docs`, `/redoc`, `/openapi.json`) **désactivée en production**.
- `SECRET_KEY` obligatoire et refusée si valeur par défaut en production (échec au démarrage).
- Cookies : `HttpOnly`, `SameSite=Lax`, `Secure` en production. CSRF : jeton par session, vérifié sur toute méthode non idempotente (formulaires + en-tête `X-CSRF-Token` pour HTMX). Redirections `next` limitées aux chemins internes. Verrouillage après 5 échecs de connexion. Limites slowapi sur connexion, inscription, publication, votes, vérifications, IA (phases suivantes).
- Contenu utilisateur : Markdown → HTML → **nh3** (liste blanche), jamais `|safe` sur du contenu non assaini.
- Les journaux ne contiennent jamais de secret, de mot de passe, de jeton ni d'en-tête `Authorization`.
- Conteneurs : utilisateur non root, image `python:3.12-slim`, pas d'outils de build dans l'image finale.

### 8. Direction design et frontend

Max est designer : vise un rendu **propre, sobre, rapide et professionnel**, au niveau d'un produit, pas d'un template.

- **Identité africaine sans clichés** : pas de masques, de tam-tams, de savanes, de silhouettes du continent en fond, ni de wax partout. L'identité passe par : une palette chaude et assumée, une typographie nette, un **motif géométrique discret** inspiré des textiles (ex. frise de losanges / triangles en SVG < 1 Ko, utilisée en filet ou en séparateur, jamais en fond chargé), des exemples concrets locaux (FCFA, +237, Yaoundé, Dakar, Abidjan), et un ton chaleureux et direct.
- **Palette (tokens dans `@theme`)** : fond blanc cassé chaud (≈ `#FAF7F2`), texte quasi noir chaud (≈ `#1C1917`), **primaire vert profond** (≈ `#0F6B4F`), **accent ocre / safran** (≈ `#D9922E`), rouge terre pour les erreurs (≈ `#B3412E`). Couleurs d'état dédiées : Fonctionne (vert), Cassée / Cassée (auto) (rouge), À re-vérifier (ambre). Vérifie un **contraste AA** (4,5:1) pour tout texte. Thème sombre via `prefers-color-scheme` si ça reste léger.
- **Typographie** : **pile de polices système** uniquement (aucune police web : poids et licence). Police à chasse fixe système pour le code. Échelle typographique claire (14/16/18/22/28/36).
- **Mobile-first** : conçu d'abord pour un écran de 360 px sur un Android d'entrée de gamme ; cibles tactiles ≥ 44 px ; une colonne sur mobile, deux à partir de `md`.
- **Accessibilité** : HTML sémantique (`header`, `nav`, `main`, `footer`, titres hiérarchiques), lien « Aller au contenu », `:focus-visible` bien visible, labels sur tous les champs, `lang="fr"`, textes alternatifs, `prefers-reduced-motion` respecté, pas d'information portée par la couleur seule (badge = icône + texte).
- **Composants du design system** (dans `templates/partials/` + classes Tailwind cohérentes) : boutons (primaire, secondaire, fantôme), champs de formulaire avec erreurs, carte de recette, **badge d'état** (4 variantes), étiquette fournisseur, message flash, pagination, état vide, bloc de code. Crée une page interne `/_design` (désactivée en production) qui affiche tous les composants : elle servira à Max pour valider le style.
- **Performance** : budget **50 Ko transférés par page** (HTML + CSS + JS + images, compressé). CSS Tailwind compilé et minifié (purge via les templates). Pas d'images matricielles lourdes : SVG inline ou fichiers SVG optimisés. Compression gzip (`GZipMiddleware`). Cache long sur `/static` avec nom de fichier versionné (hash ou paramètre de version).
- **Sans JS** : toutes les actions fonctionnent par liens et formulaires classiques. HTMX **améliore** (`hx-boost` sur la navigation, `hx-post` + `hx-target` pour les votes et vérifications, `hx-get` avec `hx-trigger="keyup changed delay:300ms"` pour la recherche) et le serveur répond un **fragment** si l'en-tête `HX-Request` est présent, la **page complète** sinon. Une seule fonction utilitaire `render(request, template, context, partial=None)` gère ce choix.
- **Mode léger** : `?lite=1` pose un cookie `lite=1` (et `?lite=0` le retire) ; activé aussi si l'en-tête `Save-Data: on`. En mode léger : pas de HTMX chargé, pas d'icônes décoratives, pas de motif, listes plus compactes. Un lien visible « Mode léger » dans l'en-tête ou le pied de page.
- **Pas de JS lourd** : aucun framework JS, aucune bibliothèque d'animation ; le seul JS est `htmx.min.js` et, plus tard, l'enregistrement du service worker (fichier externe, quelques lignes).

### 9. Ordre de construction (une phase = un arrêt)

| Phase | Date | Contenu |
|---|---|---|
| **1 (maintenant)** | 12 oct. | Squelette, Docker, config, DB + Alembic, layout + design system, accueil, `/healthz`, CI, tests verts |
| 2 | 13 oct. | Modèles + migrations, inscription / connexion / déconnexion, sessions, CSRF, profil minimal |
| 3 | 14 oct. | Recettes : création, liste, détail, Markdown assaini, filtres, recherche FR + trigram |
| 4 | 15 oct. | Worker sandbox MoMo (token, requesttopay, statut), `sandbox_runs`, clés via env |
| 5 | 16 oct. | Badge « vérifié il y a X h », page `/statut`, vérification communautaire, règle d'état |
| 6 | 17 oct. | Q&R sous les recettes, votes, réponse acceptée, réputation ; v0.1 |
| 7 | 18 oct. | PWA (service worker, manifest, page hors ligne), budget 50 Ko en CI, test sans JS |
| 8 | 19 oct. | IA doublons (embeddings + repli trigram) |
| 9 | 20 oct. | IA « Adapter à ma stack » (cache, limites) |
| 10 | 21 oct. | Durcissement sécurité, classement des contributeurs, licences, README |

### 10. PHASE 1 — à faire maintenant

Livre exactement ceci, puis **arrête-toi** :

1. **Fichiers de projet** : `pyproject.toml` (config ruff + pytest), `requirements.txt` et `requirements-dev.txt` épinglés (uniquement les dépendances nécessaires à la phase 1 : fastapi, uvicorn[standard] — vérifie les licences des extras —, pydantic-settings, sqlalchemy[asyncio], asyncpg, alembic, jinja2, python-multipart, itsdangerous ; dev : pytest, pytest-asyncio, httpx, ruff, pip-licenses).
2. **`app/config.py`** : `Settings` avec toutes les variables de `.env.example` (les clés MoMo / IA facultatives), validation de `SECRET_KEY` en production, `get_settings()` avec `lru_cache`.
3. **`app/db.py`** : moteur async, `async_sessionmaker`, dépendance `get_session()`, `Base` déclarative.
4. **`app/main.py`** : `create_app()` qui monte `/static`, les templates, `GZipMiddleware`, `TrustedHostMiddleware`, le middleware d'en-têtes de sécurité, le middleware « mode léger » (expose `request.state.lite`), les gestionnaires 404/500 HTML, et les routeurs `health` et `pages`. Docs OpenAPI désactivées en production.
5. **`GET /healthz`** : JSON `{"status": "ok", "db": "ok"|"error", "version": "…"}` ; exécute `SELECT 1` avec un délai court ; code 200 si tout va bien, 503 si la base est injoignable.
6. **Alembic async** : `alembic.ini`, `migrations/env.py` (lit `DATABASE_URL` depuis les settings), et une **première migration** qui crée les extensions `pg_trgm` et `unaccent`, puis tente `vector` sans faire échouer la migration si elle est indisponible (journalise un avertissement).
7. **Design system + layout** : `static/src/app.css` (tokens `@theme`, couches de base, composants), `scripts/get_tailwind.sh` (télécharge le CLI autonome épinglé pour l'OS courant), `templates/base.html` (en-tête avec nom du projet et lien Mode léger, `main`, pied de page avec mention CADEV 2026 et emplacement du badge CI), partials des composants listés au §8, et la page `/_design` (hors production).
8. **Page d'accueil `/`** : héros court (« Les recettes d'intégration africaines qui marchent vraiment »), barre de recherche (formulaire GET vers `/recettes`, page non encore implémentée → 404 propre acceptable), section « Comment ça marche » en 3 étapes (Recette → Vérifiée → Adaptée), bloc d'aperçu « Statut MTN MoMo sandbox » avec données **factices clairement marquées** « aperçu », 3 cartes de recettes **d'exemple** codées en dur et marquées comme exemples, appel à contribution. Page 404 et page « Hors ligne » (`offline.html`, non encore servie par un service worker).
9. **Worker** : `worker/main.py` démarre APScheduler et planifie un job « heartbeat » toutes les `SANDBOX_INTERVAL_MINUTES` qui ne fait que journaliser (le vrai job MoMo arrive en phase 4). Il s'arrête proprement sur SIGTERM.
10. **Docker** : `Dockerfile` multi-étapes (étape de build CSS avec le CLI Tailwind, étape finale `python:3.12-slim`, utilisateur non root, `HEALTHCHECK` sur `/healthz`) ; `docker-compose.yml` avec `db` (image `pgvector/pgvector:pg16`, volume, healthcheck `pg_isready`), `app` (uvicorn, port 8000, dépend de db en bonne santé, exécute `alembic upgrade head` au démarrage via une commande d'entrée simple et lisible) et `worker` (même image, commande `python -m worker.main`). Variables via `env_file: .env`.
11. **Scripts** : `scripts/check_licenses.py` (lance `pip-licenses --format=json`, échoue si une licence contient GPL, LGPL ou AGPL, signale en avertissement MPL/EPL/CDDL et « UNKNOWN », écrit la table dans `THIRD_PARTY_LICENSES.md` en conservant l'en-tête existant) ; `scripts/page_budget.py` (interroge une URL donnée, mesure la taille compressée de la page + CSS + JS qu'elle référence, échoue au-delà de 50 Ko ; en phase 1, vérifie seulement `/` ; `/_design` est exclu).
12. **Tests** (`pytest`, tous verts) : `/healthz` (200 avec base, 503 simulé sans base), `/` renvoie 200 avec `lang="fr"` et les en-têtes de sécurité, fragment vs page complète selon `HX-Request` (sur une route de démonstration simple), mode léger via `?lite=1` et via `Save-Data`, 404 HTML, `Settings` refuse la `SECRET_KEY` par défaut en production.
13. **CI** `.github/workflows/ci.yml` : déclenchée sur push et pull_request ; jobs `lint` (ruff check + format --check), `test` (service PostgreSQL `pgvector/pgvector:pg16`, `alembic upgrade head`, pytest), `licenses` (installe requirements, lance `check_licenses.py`), `budget` (construit le CSS, lance l'app, exécute `page_budget.py`) ; job `deploy` présent mais **désactivé** (`if: false` + commentaire `TODO Datacloud`) tant que l'offre Datacloud n'est pas choisie. Actions épinglées par version majeure, permissions minimales (`contents: read`).
14. Mets à jour la ligne « Phase 1 » dans `AI_USAGE.md` (fichiers générés, niveau G) et, si besoin, le README (commandes réelles).

**Critères de fin de phase 1** : `docker compose up --build` démarre les 3 services sans erreur ; `http://localhost:8000/` s'affiche bien sur mobile et sans JS ; `/healthz` renvoie `db: ok` ; `ruff check .` et `pytest` passent ; la page d'accueil fait moins de 50 Ko transférés ; aucune dépendance non permissive ; aucun secret dans le dépôt.

### 11. Format de ton compte rendu à chaque fin de phase

Arrête-toi et écris, en français :

1. **Résumé** : ce qui a été fait, en 5 à 10 puces.
2. **Fichiers** créés / modifiés (arborescence courte).
3. **Dépendances ajoutées** : tableau `nom | version | licence | raison`. Signale toute licence douteuse.
4. **Commandes à lancer** par Max, dans l'ordre, pour construire, migrer, tester et voir le résultat.
5. **Explications pour maîtriser le code** : pour chaque morceau non trivial (fabrique d'app, async SQLAlchemy, env.py Alembic, middlewares, CSP + HTMX, Dockerfile multi-étapes, CI), 3 à 6 phrases simples « ce que ça fait / pourquoi / ce qui casserait si on l'enlève ». Termine par **5 questions qu'un jury pourrait poser** sur cette phase, avec une réponse courte.
6. **Points ouverts / décisions à prendre** par Max.
7. **Proposition de message de commit.**

N'enchaîne jamais sur la phase suivante sans que Max te le demande.

---

## PROMPT PHASE 2

> À coller quand la phase 1 est relue, comprise et commitée.

Phase 1 validée, merci. Passe à la **phase 2 (13 oct.)** en respectant toutes les règles du prompt initial (licences permissives uniquement, pas de psycopg, code original et expliqué, secrets en env, design system existant, < 50 Ko, sans JS, arrêt et compte rendu en fin de phase).

À livrer :
1. **Modèles SQLAlchemy 2** de tout le modèle de données (§5) dans `app/models/`, avec enums, contraintes d'unicité, index (GIN sur `search_vector`, trigram sur les titres, `(provider, country, status)`), et colonne `embedding` en `vector` si l'extension existe, sinon JSON (choisis une approche simple et explique-la).
2. **Migration Alembic** générée puis relue à la main (triggers ou colonnes générées pour `search_vector` en configuration `french` + `unaccent`) ; `alembic downgrade -1` doit fonctionner.
3. **Auth** : inscription (pseudo, email, mot de passe ≥ 10 caractères, pays ISO2 dans une liste de pays africains + « Autre »), connexion, déconnexion ; mots de passe Argon2id via pwdlib (vérifie la licence) ; session par cookie signé itsdangerous (rotation à la connexion, expiration) ; dépendances `get_current_user` / `require_user` ; verrouillage 15 min après 5 échecs ; message d'erreur identique pour « email inconnu » et « mauvais mot de passe » ; redirection `?next=` limitée aux chemins internes.
4. **CSRF** : jeton par session, champ caché dans tous les formulaires (macro Jinja), en-tête `X-CSRF-Token` pour HTMX via `hx-headers` sur le `body`, vérification sur POST/PUT/PATCH/DELETE, réponse 403 propre.
5. **slowapi** sur connexion et inscription (vérifie la licence), avec message en français.
6. **Profil public minimal** `/u/{username}` (pseudo, pays, réputation, date d'inscription) et menu utilisateur dans l'en-tête.
7. **Tests** : inscription, connexion OK/KO, verrouillage, CSRF manquant → 403, `next` externe refusé, unicité email/pseudo, migration up/down en CI.
8. Pages formulaires conformes au design system (labels, erreurs inline, accessibles, mobiles), fonctionnant sans JS.

Termine avec le compte rendu standard (§11), y compris les 5 questions de jury sur l'authentification et la sécurité.
