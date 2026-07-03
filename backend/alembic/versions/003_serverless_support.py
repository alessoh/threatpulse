"""auth_attempts table for serverless rate limiting; one playbook per threat

Revision ID: 003
Revises: 002
Create Date: 2026-07-03
"""
from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "auth_attempts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ip", sa.String(64), nullable=False),
        sa.Column("attempted_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_auth_attempts_ip", "auth_attempts", ["ip"])
    op.create_index("ix_auth_attempts_attempted_at", "auth_attempts", ["attempted_at"])

    # On-demand playbook generation can race between two concurrent requests;
    # the unique index makes the second insert fail cleanly instead of
    # storing a duplicate.
    op.create_index("uq_playbooks_threat_id", "playbooks", ["threat_id"], unique=True)


def downgrade() -> None:
    op.drop_index("uq_playbooks_threat_id", table_name="playbooks")
    op.drop_index("ix_auth_attempts_attempted_at", table_name="auth_attempts")
    op.drop_index("ix_auth_attempts_ip", table_name="auth_attempts")
    op.drop_table("auth_attempts")
