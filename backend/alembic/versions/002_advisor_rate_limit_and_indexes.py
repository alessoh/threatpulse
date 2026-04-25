"""advisor rate limit columns and threat indexes

Revision ID: 002
Revises: 001
Create Date: 2026-04-25
"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("advisor_count_today", sa.Integer(), server_default=sa.text("0")))
    op.add_column("users", sa.Column("advisor_count_date", sa.String(10), server_default=""))

    op.create_index("ix_threats_severity", "threats", ["severity"])
    op.create_index("ix_threats_threat_type", "threats", ["threat_type"])
    op.create_index("ix_threats_is_active", "threats", ["is_active"])
    op.create_index("ix_threats_last_updated", "threats", ["last_updated"])


def downgrade() -> None:
    op.drop_index("ix_threats_last_updated", table_name="threats")
    op.drop_index("ix_threats_is_active", table_name="threats")
    op.drop_index("ix_threats_threat_type", table_name="threats")
    op.drop_index("ix_threats_severity", table_name="threats")

    op.drop_column("users", "advisor_count_date")
    op.drop_column("users", "advisor_count_today")
