"""
Startup ingestion runner.

Why: on free hosting tiers the filesystem is often ephemeral across
redeploys/restarts, so the ChromaDB persistence directory can be wiped.
The knowledge base is static (fixed textbook PDFs shipped in the repo),
so it's cheap and safe to check-and-rebuild it every time the app
starts. `ensure_ingested()` in the ingestion script already skips any
role collection that's already populated, so this is a no-op on a
"warm" deploy and only does real work after a disk wipe or first boot.
"""
import logging

logger = logging.getLogger("ingestion_runner")


def run_startup_ingestion() -> None:
    try:
        from ingestion.ingest_knowledge_base import ensure_ingested
        ensure_ingested()
    except Exception:
        # Don't crash the whole app if ingestion fails (e.g. a PDF is
        # missing in this environment) -- log it clearly instead, since
        # the alternative (app won't boot at all) is worse for a demo.
        logger.exception("Startup knowledge base ingestion failed.")
