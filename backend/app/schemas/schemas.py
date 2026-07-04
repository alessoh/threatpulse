from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ── Auth ──

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str = ""
    company: str = ""

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    company: str
    tier: str
    industry: str
    tech_stack: str
    created_at: datetime
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    tech_stack: Optional[str] = None
    notify_critical: Optional[bool] = None
    notify_high: Optional[bool] = None
    notify_weekly_digest: Optional[bool] = None


# ── Threats ──

class ThreatSummary(BaseModel):
    id: int
    name: str
    slug: str
    severity: str
    threat_type: str
    category: str = "conventional"  # "agent" | "conventional"
    tags: str
    summary: str
    cvss_score: Optional[float]
    is_active: bool
    first_seen: datetime
    last_updated: datetime
    class Config:
        from_attributes = True

class ThreatDetail(ThreatSummary):
    technical_analysis: str
    affected_systems: str
    iocs: str
    remediation_steps: str
    source_urls: str
    cve_ids: str
    industries_affected: str

class ThreatListResponse(BaseModel):
    threats: List[ThreatSummary]
    total: int
    page: int
    per_page: int


# ── Playbooks ──

class PlaybookResponse(BaseModel):
    id: int
    threat_id: int
    title: str
    executive_summary: str
    technical_details: str
    steps_json: str
    yara_rules: str
    config_templates: str
    tier_required: str
    class Config:
        from_attributes = True


# ── AI Advisor ──

class AdvisorRequest(BaseModel):
    message: str
    threat_id: Optional[int] = None
    conversation_history: List[dict] = []

class AdvisorResponse(BaseModel):
    response: str


# ── Subscription ──

class CheckoutRequest(BaseModel):
    price_id: str

class CheckoutResponse(BaseModel):
    checkout_url: str

class PortalResponse(BaseModel):
    portal_url: str


# ── Dashboard Stats ──

class DashboardStats(BaseModel):
    critical_count: int
    high_count: int
    active_campaigns: int
    sources_monitored: int
    critical_delta: int
    high_delta: int
    # Agent-first pivot: the dashboard leads with these; the fields above are
    # kept so older clients and the /v1 API keep working unchanged.
    agent_count: int = 0
    agent_critical_count: int = 0
    agent_new_week: int = 0
    conventional_count: int = 0
