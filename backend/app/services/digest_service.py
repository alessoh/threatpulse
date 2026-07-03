"""Weekly digest, shared by the cron route and scripts/weekly_digest.py.

Idempotent via alert_logs: a user who already received a digest in the past
six days is skipped, so overlapping cron firings or manual re-runs cannot
double-send.
"""

from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session

from app.models.user import User, Threat, AlertLog
from app.services.ai_service import generate_weekly_digest
from app.services.email_service import send_weekly_digest

DIGEST_ALERT_TYPE = "weekly_digest"
DIGEST_COOLDOWN_DAYS = 6


def send_weekly_digest_to_subscribers(db: Session) -> dict:
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    threats = (
        db.query(Threat)
        .filter(Threat.last_updated >= week_ago, Threat.is_active == True)
        .order_by(Threat.severity.desc(), Threat.last_updated.desc())
        .limit(10)
        .all()
    )

    if not threats:
        return {"status": "skipped", "reason": "no threats in the past week", "sent": 0}

    digest_body = generate_weekly_digest(threats)

    subscribers = (
        db.query(User)
        .filter(User.tier.in_(["pro", "enterprise"]), User.notify_weekly_digest == True)
        .all()
    )

    cooldown_cutoff = now - timedelta(days=DIGEST_COOLDOWN_DAYS)
    sent = 0
    skipped = 0
    failed = 0
    for user in subscribers:
        recent = db.query(AlertLog.id).filter(
            AlertLog.user_id == user.id,
            AlertLog.alert_type == DIGEST_ALERT_TYPE,
            AlertLog.sent_at >= cooldown_cutoff,
        ).first()
        if recent:
            skipped += 1
            continue
        try:
            send_weekly_digest(user, digest_body)
            db.add(AlertLog(user_id=user.id, threat_id=None, alert_type=DIGEST_ALERT_TYPE))
            db.commit()
            sent += 1
        except Exception as e:
            db.rollback()
            failed += 1
            print(f"Digest failed for {user.email}: {e}")

    return {"status": "ok", "sent": sent, "skipped": skipped, "failed": failed,
            "subscribers": len(subscribers), "threats": len(threats)}
