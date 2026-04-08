from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class TierEnum(str, enum.Enum):
    free = "free"
    pro = "pro"
    enterprise = "enterprise"


class SeverityEnum(str, enum.Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), default="")
    company = Column(String(255), default="")
    tier = Column(String(20), default="free")
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    industry = Column(String(100), default="")
    tech_stack = Column(Text, default="")
    notify_critical = Column(Boolean, default=True)
    notify_high = Column(Boolean, default=True)
    notify_weekly_digest = Column(Boolean, default=True)
    api_key = Column(String(64), nullable=True, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    bookmarks = relationship("Bookmark", back_populates="user")


class Threat(Base):
    __tablename__ = "threats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True)
    severity = Column(String(20), nullable=False)
    threat_type = Column(String(50), nullable=False)
    tags = Column(Text, default="")
    summary = Column(Text, nullable=False)
    technical_analysis = Column(Text, default="")
    affected_systems = Column(Text, default="")
    iocs = Column(Text, default="")
    remediation_steps = Column(Text, default="")
    source_urls = Column(Text, default="")
    cvss_score = Column(Float, nullable=True)
    cve_ids = Column(Text, default="")
    industries_affected = Column(Text, default="")
    is_active = Column(Boolean, default=True)
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    bookmarks = relationship("Bookmark", back_populates="threat")


class Playbook(Base):
    __tablename__ = "playbooks"

    id = Column(Integer, primary_key=True, index=True)
    threat_id = Column(Integer, ForeignKey("threats.id"), nullable=False)
    title = Column(String(255), nullable=False)
    executive_summary = Column(Text, nullable=False)
    technical_details = Column(Text, default="")
    steps_json = Column(Text, default="[]")
    yara_rules = Column(Text, default="")
    config_templates = Column(Text, default="")
    tier_required = Column(String(20), default="pro")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    threat = relationship("Threat")


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    threat_id = Column(Integer, ForeignKey("threats.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="bookmarks")
    threat = relationship("Threat", back_populates="bookmarks")


class AlertLog(Base):
    __tablename__ = "alert_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    threat_id = Column(Integer, ForeignKey("threats.id"), nullable=True)
    alert_type = Column(String(50), nullable=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())


class ScraperLog(Base):
    __tablename__ = "scraper_logs"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)
    items_found = Column(Integer, default=0)
    items_new = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    run_at = Column(DateTime(timezone=True), server_default=func.now())
