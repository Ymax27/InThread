# syntax=docker/dockerfile:1
# Image unique, deux binaires : l'API (uvicorn) et le worker (APScheduler).
# Le CSS Tailwind est compilé dans une étape dédiée — aucun Node dans l'image finale.

### Étape 1 — dépendances Python, isolées dans un venv ###
FROM python:3.12-slim AS deps

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt ./
RUN pip install -r requirements.txt

### Étape 2 — CSS Tailwind (binaire autonome téléchargé, sortie minifiée) ###
FROM debian:bookworm-slim AS css

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
# Le CLI scanne les sources (templates + static/src) pour garder uniquement
# les classes utilisées : on lui donne tout le dossier app/.
COPY scripts/get_tailwind.sh ./scripts/get_tailwind.sh
COPY app/ ./app/
RUN chmod +x scripts/get_tailwind.sh \
    && ./scripts/get_tailwind.sh \
    && ./bin/tailwindcss -i app/static/src/app.css -o /tmp/app.css --minify \
    && cp /tmp/app.css app/static/css/app.css

### Étape « dev » — image de développement et de test (profil `dev` de compose) ###
# Mêmes dépendances que l'étape deps, plus requirements-dev.txt et les tests.
# Utilisation : docker compose --profile dev run --rm dev pytest
FROM deps AS dev

COPY requirements-dev.txt ./
RUN pip install -r requirements-dev.txt

WORKDIR /opt/mboa
COPY alembic.ini pyproject.toml ./
COPY app/ ./app/
COPY migrations/ ./migrations/
COPY scripts/ ./scripts/
COPY tests/ ./tests/
COPY worker/ ./worker/

CMD ["pytest"]

### Étape 3 — image finale, minimale, non-root ###
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

# Utilisateur non-root (règle de sécurité §7).
RUN useradd --create-home --uid 10001 app

WORKDIR /opt/mboa

# venv issu de l'étape deps, code applicatif, CSS compilé.
COPY --from=deps /opt/venv /opt/venv
COPY alembic.ini ./
COPY app/ ./app/
COPY migrations/ ./migrations/
COPY scripts/ ./scripts/
COPY worker/ ./worker/
COPY --from=css /src/app/static/css/app.css ./app/static/css/app.css

USER app
EXPOSE 8000

# Santé du conteneur lui-même (compose a sa propre vérification, plus fine).
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=3)"

# Le CMD peut être remplacé par `python -m worker.main` (service worker de compose).
CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
