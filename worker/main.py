"""Point d'entrée du worker : APScheduler + job « heartbeat ».

Phase 1 : le job ne fait que journaliser, il sert à vérifier que le conteneur,
la planification et les journaux fonctionnent. Le vrai job (parcours sandbox
MTN MoMo : token → requesttopay → statut) arrive en phase 4, dans `app/sandbox/`.
"""

from __future__ import annotations

import asyncio
import logging
import signal

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import get_settings
from app.logging import configure_logging

log = logging.getLogger("worker")


def heartbeat() -> None:
    """Job horaire : preuve de vie. Remplacé par le test sandbox en phase 4."""
    log.info("heartbeat — worker en vie (aucun test sandbox configuré en phase 1)")


def build_scheduler(interval_minutes: int) -> AsyncIOScheduler:
    """Fabrique le planificateur (fonction isolée pour pouvoir la tester)."""
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(
        heartbeat,
        "interval",
        minutes=interval_minutes,
        id="heartbeat",
        max_instances=1,  # jamais deux heartbeats en parallèle
        coalesce=True,  # un retard rattrapé = un seul envoi
    )
    return scheduler


async def run() -> None:
    """Démarre le worker et attend SIGTERM/SIGINT pour s'arrêter proprement."""
    settings = get_settings()
    configure_logging(settings)
    interval = max(1, settings.sandbox_interval_minutes)

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop.set)

    scheduler = build_scheduler(interval)
    scheduler.start()
    log.info("worker démarré : heartbeat toutes les %s minutes", interval)

    await stop.wait()  # docker compose envoie SIGTERM à l'arrêt

    scheduler.shutdown(wait=False)
    log.info("worker arrêté proprement")


def main() -> None:
    """Exécutable : `python -m worker.main`."""
    try:
        asyncio.run(run())
    except KeyboardInterrupt:  # Ctrl-C en local
        pass


if __name__ == "__main__":
    main()
