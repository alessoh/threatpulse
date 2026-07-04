"""Add daily_insights table for the Gemini-generated dashboard insight.

Written defensively: the insight service also creates this table on demand
(checkfirst) so production doesn't require a manual migration run, and this
migration skips creation if the table already exists.

Revision ID: 004
Revises: 003
"""

import sqlalchemy as sa
from alembic import op

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    if sa.inspect(bind).has_table("daily_insights"):
        return
    op.create_table(
        "daily_insights",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("date", sa.String(10), nullable=False, unique=True, index=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("model", sa.String(100), server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("daily_insights")
