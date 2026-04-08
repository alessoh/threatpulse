"""
Send weekly threat digest emails to all pro/enterprise subscribers.
Run via cron: 0 9 * * 1 python -m scripts.weekly_digest
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timezone, timedelta
from app.core.database import SessionLocal
from app.models.user import User, Threat
from app.services.ai_service import generate_weekly_digest
from app.services.email_service import send_weekly_digest

def main():
    db = SessionLocal()
    try:
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        threats = (
            db.query(Threat)
            .filter(Threat.last_updated >= week_ago, Threat.is_active == True)
            .order_by(Threat.severity.desc(), Threat.last_updated.desc())
            .limit(10)
            .all()
        )

        if not threats:
            print("No threats from the past week. Skipping digest.")
            return

        print(f"Generating digest from {len(threats)} threats...")
        digest_body = generate_weekly_digest(threats)

        subscribers = (
            db.query(User)
            .filter(User.tier.in_(["pro", "enterprise"]), User.notify_weekly_digest == True)
            .all()
        )

        print(f"Sending to {len(subscribers)} subscribers...")
        sent = 0
        for user in subscribers:
            try:
                send_weekly_digest(user, digest_body)
                sent += 1
            except Exception as e:
                print(f"  Failed for {user.email}: {e}")

        print(f"Done. Sent {sent}/{len(subscribers)} digests.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
