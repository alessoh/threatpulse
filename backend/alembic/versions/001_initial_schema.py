"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-04-08
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), server_default=""),
        sa.Column("company", sa.String(255), server_default=""),
        sa.Column("tier", sa.String(20), server_default="free"),
        sa.Column("stripe_customer_id", sa.String(255), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(255), nullable=True),
        sa.Column("industry", sa.String(100), server_default=""),
        sa.Column("tech_stack", sa.Text(), server_default=""),
        sa.Column("notify_critical", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("notify_high", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("notify_weekly_digest", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("api_key", sa.String(64), nullable=True, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "threats",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("threat_type", sa.String(50), nullable=False),
        sa.Column("tags", sa.Text(), server_default=""),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("technical_analysis", sa.Text(), server_default=""),
        sa.Column("affected_systems", sa.Text(), server_default=""),
        sa.Column("iocs", sa.Text(), server_default=""),
        sa.Column("remediation_steps", sa.Text(), server_default=""),
        sa.Column("source_urls", sa.Text(), server_default=""),
        sa.Column("cvss_score", sa.Float(), nullable=True),
        sa.Column("cve_ids", sa.Text(), server_default=""),
        sa.Column("industries_affected", sa.Text(), server_default=""),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("first_seen", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_updated", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "playbooks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("threat_id", sa.Integer(), sa.ForeignKey("threats.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("executive_summary", sa.Text(), nullable=False),
        sa.Column("technical_details", sa.Text(), server_default=""),
        sa.Column("steps_json", sa.Text(), server_default="[]"),
        sa.Column("yara_rules", sa.Text(), server_default=""),
        sa.Column("config_templates", sa.Text(), server_default=""),
        sa.Column("tier_required", sa.String(20), server_default="pro"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "bookmarks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("threat_id", sa.Integer(), sa.ForeignKey("threats.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "alert_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("threat_id", sa.Integer(), sa.ForeignKey("threats.id"), nullable=True),
        sa.Column("alert_type", sa.String(50), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "scraper_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("source", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("items_found", sa.Integer(), server_default=sa.text("0")),
        sa.Column("items_new", sa.Integer(), server_default=sa.text("0")),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("run_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("scraper_logs")
    op.drop_table("alert_logs")
    op.drop_table("bookmarks")
    op.drop_table("playbooks")
    op.drop_table("threats")
    op.drop_table("users")
