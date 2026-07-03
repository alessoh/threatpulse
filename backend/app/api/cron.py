"""Cron endpoints, invoked by Vercel Cron on the schedules in vercel.json.

Vercel sends "Authorization: Bearer <CRON_SECRET>" when the CRON_SECRET
environment variable is set on the project; every route here verifies it, so
random visitors cannot trigger paid Claude calls or outbound email.

Each route processes a bounded batch and exits, so a run always fits inside
the function's maxDuration. Deduplication happens before synthesis, so
steady-state runs only pay for genuinely new items.
"""

import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db

router = APIRouter()

# Per-source batch caps keep one cron invocation well inside maxDuration even
# on a cold database. Anything not processed this run is picked up next run.
CISA_BATCH = 5
NVD_BATCH = 5
RSS_BATCH_PER_FEED = 3


def verify_cron_secret(authorization: str = Header("")):
    settings = get_settings()
    if not settings.cron_secret:
        raise HTTPException(503, "CRON_SECRET is not configured on the server")
    expected = f"Bearer {settings.cron_secret}"
    if not secrets.compare_digest(authorization, expected):
        raise HTTPException(401, "Invalid cron authorization")


@router.get("/cron/scrape-all", dependencies=[Depends(verify_cron_secret)])
def cron_scrape_all(db: Session = Depends(get_db)):
    """Run every collector once with bounded batches."""
    from app.scrapers.collectors import scrape_cisa_kev, scrape_nvd_recent, scrape_rss_feed, RSS_FEEDS
    from app.scrapers.agent_collectors import run_agent_scrapers

    started = datetime.now(timezone.utc)
    results = {}
    results["cisa_kev"] = _safe(lambda: scrape_cisa_kev(db, limit=CISA_BATCH))
    results["nvd"] = _safe(lambda: scrape_nvd_recent(db, limit=NVD_BATCH))
    for name, url in RSS_FEEDS.items():
        results[f"rss:{name}"] = _safe(lambda u=url, n=name: scrape_rss_feed(db, u, n, limit=RSS_BATCH_PER_FEED))
    results["agent_threats"] = _safe(lambda: run_agent_scrapers(db))

    return {
        "status": "ok",
        "started": started.isoformat(),
        "finished": datetime.now(timezone.utc).isoformat(),
        "new_threats": results,
    }


@router.get("/cron/scrape-agents", dependencies=[Depends(verify_cron_secret)])
def cron_scrape_agents(db: Session = Depends(get_db)):
    """Agent-threat collectors only. Not scheduled by default; add it to
    vercel.json crons for a more frequent agent-focused cadence (Pro plan)."""
    from app.scrapers.agent_collectors import run_agent_scrapers

    return {"status": "ok", "new_threats": _safe(lambda: run_agent_scrapers(db))}


@router.get("/cron/weekly-digest", dependencies=[Depends(verify_cron_secret)])
def cron_weekly_digest(db: Session = Depends(get_db)):
    from app.services.digest_service import send_weekly_digest_to_subscribers

    return send_weekly_digest_to_subscribers(db)


def _safe(fn):
    """Run one collector, converting an exception into a reported error so a
    single failing source never aborts the whole cron run."""
    try:
        return fn()
    except Exception as exc:
        print(f"[cron] collector failed: {exc}")
        return {"error": str(exc)}
