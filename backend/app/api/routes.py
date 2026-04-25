import secrets
import stripe as stripe_lib
from datetime import datetime, timezone, timedelta, date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Query, Header
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.core.database import get_db
from app.core.config import get_settings
from app.core.auth import hash_password, verify_password, create_access_token, get_current_user, require_tier
from app.models.user import User, Threat, Playbook, Bookmark
from app.schemas.schemas import (
    RegisterRequest, LoginRequest, AuthResponse, UserResponse, UserUpdate,
    ThreatSummary, ThreatDetail, ThreatListResponse, PlaybookResponse,
    AdvisorRequest, AdvisorResponse, CheckoutRequest, CheckoutResponse,
    PortalResponse, DashboardStats,
)
from app.services import ai_service, stripe_service

router = APIRouter()


# ══════════════════════════════════════
# Simple in-memory rate limit for auth endpoints
# (Replace with Redis-backed limiter for multi-instance deployments)
# ══════════════════════════════════════

_auth_attempts: dict[str, list[datetime]] = {}
AUTH_WINDOW_SECONDS = 900  # 15 minutes
AUTH_MAX_ATTEMPTS = 8


def _check_auth_rate_limit(request: Request):
    ip = request.client.host if request.client else "unknown"
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(seconds=AUTH_WINDOW_SECONDS)
    bucket = [t for t in _auth_attempts.get(ip, []) if t > cutoff]
    if len(bucket) >= AUTH_MAX_ATTEMPTS:
        raise HTTPException(429, "Too many attempts. Try again in 15 minutes.")
    bucket.append(now)
    _auth_attempts[ip] = bucket


# ══════════════════════════════════════
# AUTH
# ══════════════════════════════════════

@router.post("/auth/register", response_model=AuthResponse)
def register(req: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    _check_auth_rate_limit(request)
    if len(req.password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(400, "Email already registered")
    user = User(
        email=req.email,
        password_hash=hash_password(req.password),
        full_name=req.full_name,
        company=req.company,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id, user.email)
    return AuthResponse(access_token=token, user=UserResponse.model_validate(user))


@router.post("/auth/login", response_model=AuthResponse)
def login(req: LoginRequest, request: Request, db: Session = Depends(get_db)):
    _check_auth_rate_limit(request)
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    token = create_access_token(user.id, user.email)
    return AuthResponse(access_token=token, user=UserResponse.model_validate(user))


@router.get("/auth/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    return UserResponse.model_validate(user)


@router.patch("/auth/me", response_model=UserResponse)
def update_me(req: UserUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


@router.post("/auth/api-key")
def generate_api_key(user: User = Depends(require_tier("enterprise")), db: Session = Depends(get_db)):
    user.api_key = "tp_" + secrets.token_urlsafe(32)
    db.commit()
    return {"api_key": user.api_key}


# ══════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════

@router.get("/dashboard/stats", response_model=DashboardStats)
def dashboard_stats(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    two_weeks_ago = now - timedelta(days=14)

    critical = db.query(func.count(Threat.id)).filter(Threat.severity == "critical", Threat.is_active == True).scalar()
    high = db.query(func.count(Threat.id)).filter(Threat.severity == "high", Threat.is_active == True).scalar()
    active = db.query(func.count(Threat.id)).filter(Threat.is_active == True, Threat.last_updated >= week_ago).scalar()

    prev_critical = db.query(func.count(Threat.id)).filter(
        Threat.severity == "critical", Threat.first_seen.between(two_weeks_ago, week_ago)
    ).scalar()
    prev_high = db.query(func.count(Threat.id)).filter(
        Threat.severity == "high", Threat.first_seen.between(two_weeks_ago, week_ago)
    ).scalar()

    return DashboardStats(
        critical_count=critical,
        high_count=high,
        active_campaigns=active,
        sources_monitored=86,
        critical_delta=critical - prev_critical,
        high_delta=high - prev_high,
    )


# ══════════════════════════════════════
# THREATS
# ══════════════════════════════════════

@router.get("/threats", response_model=ThreatListResponse)
def list_threats(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    severity: Optional[str] = None,
    threat_type: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Threat).filter(Threat.is_active == True)

    if severity:
        q = q.filter(Threat.severity == severity)
    if threat_type:
        q = q.filter(Threat.threat_type == threat_type)
    if search:
        q = q.filter(Threat.name.ilike(f"%{search}%") | Threat.summary.ilike(f"%{search}%"))

    total = q.count()
    threats = q.order_by(desc(Threat.last_updated)).offset((page - 1) * per_page).limit(per_page).all()

    return ThreatListResponse(
        threats=[ThreatSummary.model_validate(t) for t in threats],
        total=total, page=page, per_page=per_page,
    )


@router.get("/threats/{slug}", response_model=ThreatDetail)
def get_threat(slug: str, db: Session = Depends(get_db)):
    threat = db.query(Threat).filter(Threat.slug == slug).first()
    if not threat:
        raise HTTPException(404, "Threat not found")
    return ThreatDetail.model_validate(threat)


@router.get("/threats/{slug}/playbook", response_model=PlaybookResponse)
def get_playbook(slug: str, user: User = Depends(require_tier("pro")), db: Session = Depends(get_db)):
    threat = db.query(Threat).filter(Threat.slug == slug).first()
    if not threat:
        raise HTTPException(404, "Threat not found")
    playbook = db.query(Playbook).filter(Playbook.threat_id == threat.id).first()
    if not playbook:
        raise HTTPException(404, "Playbook not found")
    return PlaybookResponse.model_validate(playbook)


# ══════════════════════════════════════
# AI ADVISOR (with free-tier rate limit)
# ══════════════════════════════════════

FREE_TIER_DAILY_LIMIT = 3


@router.post("/advisor", response_model=AdvisorResponse)
def ai_advisor(req: AdvisorRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.tier == "free":
        today = date.today().isoformat()
        if user.advisor_count_date != today:
            user.advisor_count_date = today
            user.advisor_count_today = 0
        if (user.advisor_count_today or 0) >= FREE_TIER_DAILY_LIMIT:
            raise HTTPException(
                429,
                f"Free tier limit reached ({FREE_TIER_DAILY_LIMIT}/day). Upgrade to Pro for unlimited access.",
            )
        user.advisor_count_today = (user.advisor_count_today or 0) + 1
        db.commit()

    threat_context = None
    if req.threat_id:
        threat = db.query(Threat).filter(Threat.id == req.threat_id).first()
        if threat:
            threat_context = (
                f"Threat: {threat.name}\nSeverity: {threat.severity}\nSummary: {threat.summary}\n"
                f"Technical: {threat.technical_analysis}\nAffected: {threat.affected_systems}\nIOCs: {threat.iocs}"
            )

    response = ai_service.advisor_chat(req.message, threat_context, req.conversation_history)
    return AdvisorResponse(response=response)


# ══════════════════════════════════════
# AI SEARCH
# ══════════════════════════════════════

@router.get("/search")
def ai_search(q: str = Query(..., min_length=2, max_length=200), db: Session = Depends(get_db)):
    threats = db.query(Threat).filter(
        Threat.name.ilike(f"%{q}%") | Threat.summary.ilike(f"%{q}%") | Threat.cve_ids.ilike(f"%{q}%")
    ).limit(5).all()

    if threats:
        return {"results": [ThreatSummary.model_validate(t) for t in threats], "source": "database"}

    try:
        result = ai_service.synthesize_threat({"user_query": q, "source": "user_search"})
        return {"results": [result], "source": "ai"}
    except Exception as e:
        return {"results": [], "source": "error", "message": str(e)}


# ══════════════════════════════════════
# BOOKMARKS
# ══════════════════════════════════════

@router.post("/bookmarks/{threat_id}")
def add_bookmark(threat_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(Bookmark).filter(Bookmark.user_id == user.id, Bookmark.threat_id == threat_id).first()
    if existing:
        return {"status": "already bookmarked"}
    db.add(Bookmark(user_id=user.id, threat_id=threat_id))
    db.commit()
    return {"status": "bookmarked"}


@router.delete("/bookmarks/{threat_id}")
def remove_bookmark(threat_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bm = db.query(Bookmark).filter(Bookmark.user_id == user.id, Bookmark.threat_id == threat_id).first()
    if bm:
        db.delete(bm)
        db.commit()
    return {"status": "removed"}


@router.get("/bookmarks")
def list_bookmarks(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bookmarks = db.query(Bookmark).filter(Bookmark.user_id == user.id).all()
    threat_ids = [b.threat_id for b in bookmarks]
    threats = db.query(Threat).filter(Threat.id.in_(threat_ids)).all() if threat_ids else []
    return [ThreatSummary.model_validate(t) for t in threats]


# ══════════════════════════════════════
# SUBSCRIPTIONS
# ══════════════════════════════════════

@router.post("/subscribe/checkout", response_model=CheckoutResponse)
def create_checkout(req: CheckoutRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    settings = get_settings()
    url = stripe_service.create_checkout_session(
        user, req.price_id,
        success_url=f"{settings.frontend_url}/dashboard?upgrade=success",
        cancel_url=f"{settings.frontend_url}/pricing",
    )
    db.commit()
    return CheckoutResponse(checkout_url=url)


@router.post("/subscribe/portal", response_model=PortalResponse)
def create_portal(user: User = Depends(get_current_user)):
    settings = get_settings()
    if not user.stripe_customer_id:
        raise HTTPException(400, "No subscription found")
    url = stripe_service.create_portal_session(user.stripe_customer_id, f"{settings.frontend_url}/dashboard")
    return PortalResponse(portal_url=url)


@router.post("/webhook/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    try:
        return stripe_service.handle_webhook_event(payload, sig, db)
    except stripe_lib.error.SignatureVerificationError:
        raise HTTPException(401, "Invalid Stripe webhook signature")
    except ValueError:
        raise HTTPException(400, "Invalid Stripe webhook payload")
    except Exception as e:
        print(f"[stripe webhook] {e}")
        raise HTTPException(500, "Webhook processing error")


# ══════════════════════════════════════
# ENTERPRISE API (STIX format)
# ══════════════════════════════════════

def require_api_key(x_api_key: str = Header(...), db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.api_key == x_api_key, User.tier == "enterprise").first()
    if not user:
        raise HTTPException(401, "Invalid or non-enterprise API key")
    return user


@router.get("/v1/threats")
def api_threats(
    severity: Optional[str] = None,
    threat_type: Optional[str] = None,
    since: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    q = db.query(Threat).filter(Threat.is_active == True)
    if severity:
        q = q.filter(Threat.severity == severity)
    if threat_type:
        q = q.filter(Threat.threat_type == threat_type)
    if since:
        try:
            since_dt = datetime.fromisoformat(since)
            q = q.filter(Threat.last_updated >= since_dt)
        except ValueError:
            pass

    threats = q.order_by(desc(Threat.last_updated)).limit(limit).all()

    return {
        "type": "bundle",
        "id": "bundle--threatpulse",
        "objects": [
            {
                "type": "indicator",
                "id": f"indicator--tp-{t.id}",
                "name": t.name,
                "description": t.summary,
                "pattern_type": "threatpulse",
                "severity": t.severity,
                "threat_type": t.threat_type,
                "iocs": t.iocs,
                "cvss_score": t.cvss_score,
                "cve_ids": t.cve_ids,
                "remediation": t.remediation_steps,
                "modified": t.last_updated.isoformat() if t.last_updated else None,
                "created": t.created_at.isoformat() if t.created_at else None,
            }
            for t in threats
        ],
    }
