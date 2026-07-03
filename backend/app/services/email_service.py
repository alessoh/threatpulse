import html
import resend
from app.core.config import get_settings
from app.models.user import User, AlertLog
from sqlalchemy.orm import Session


def send_threat_alert(user: User, threat_name: str, severity: str, summary: str):
    settings = get_settings()
    resend.api_key = settings.resend_api_key

    safe_name = html.escape(threat_name)
    safe_severity = html.escape(severity.upper())
    safe_summary = html.escape(summary)

    resend.Emails.send({
        "from": settings.email_from,
        "to": user.email,
        "subject": f"[ThreatPulse {safe_severity}] {safe_name}",
        "html": f"""
        <div style="font-family:sans-serif;max-width:600px;margin:0 auto">
            <div style="background:#2563eb;color:white;padding:16px 24px;border-radius:8px 8px 0 0">
                <h2 style="margin:0">ThreatPulse Alert</h2>
            </div>
            <div style="padding:24px;border:1px solid #e2e8f0;border-top:none;border-radius:0 0 8px 8px">
                <div style="display:inline-block;padding:4px 10px;border-radius:4px;font-size:12px;font-weight:600;
                    background:{'#fef2f2' if severity=='critical' else '#fff7ed'};
                    color:{'#dc2626' if severity=='critical' else '#ea580c'};
                    border:1px solid {'#fecaca' if severity=='critical' else '#fed7aa'}">
                    {safe_severity}
                </div>
                <h3 style="margin:12px 0 8px">{safe_name}</h3>
                <p style="color:#64748b;line-height:1.6">{safe_summary}</p>
                <a href="{settings.frontend_url}/library" style="display:inline-block;margin-top:16px;padding:10px 24px;background:#2563eb;color:white;text-decoration:none;border-radius:6px;font-weight:600">View Full Profile</a>
            </div>
        </div>""",
    })


def send_weekly_digest(user: User, digest_body: str):
    settings = get_settings()
    resend.api_key = settings.resend_api_key

    safe_body = html.escape(digest_body)

    resend.Emails.send({
        "from": settings.email_from,
        "to": user.email,
        "subject": "[ThreatPulse] Weekly Threat Digest",
        "html": f"""
        <div style="font-family:sans-serif;max-width:600px;margin:0 auto">
            <div style="background:#2563eb;color:white;padding:16px 24px;border-radius:8px 8px 0 0">
                <h2 style="margin:0">Weekly Threat Digest</h2>
            </div>
            <div style="padding:24px;border:1px solid #e2e8f0;border-top:none;border-radius:0 0 8px 8px;color:#334155;line-height:1.7;white-space:pre-wrap">{safe_body}</div>
        </div>""",
    })


def notify_users_of_threat(db: Session, threat):
    """Send alerts to users whose preferences match this threat.

    Idempotent: each send is recorded in alert_logs and checked first, so a
    re-run or retried scrape cycle never emails the same user about the same
    threat twice.
    """
    severity = threat.severity
    users = db.query(User).filter(User.tier.in_(["pro", "enterprise"]))

    if severity == "critical":
        users = users.filter(User.notify_critical == True)
    elif severity == "high":
        users = users.filter(User.notify_high == True)
    else:
        return

    for user in users.all():
        already_sent = db.query(AlertLog.id).filter(
            AlertLog.user_id == user.id,
            AlertLog.threat_id == threat.id,
            AlertLog.alert_type == "threat_alert",
        ).first()
        if already_sent:
            continue
        try:
            send_threat_alert(user, threat.name, threat.severity, threat.summary)
            db.add(AlertLog(user_id=user.id, threat_id=threat.id, alert_type="threat_alert"))
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Failed to send alert to {user.email}: {e}")
