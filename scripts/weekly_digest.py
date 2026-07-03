"""
Send weekly threat digest emails to all pro/enterprise subscribers.

On Vercel this runs automatically via the /api/cron/weekly-digest route.
This script remains for local/manual runs: python -m scripts.weekly_digest
Sends are idempotent (tracked in alert_logs), so re-running is safe.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import SessionLocal
from app.services.digest_service import send_weekly_digest_to_subscribers


def main():
    db = SessionLocal()
    try:
        result = send_weekly_digest_to_subscribers(db)
        print(result)
    finally:
        db.close()


if __name__ == "__main__":
    main()
