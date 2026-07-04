"""Add threats.category ("agent" | "conventional") and backfill existing rows.

Part of the agent-first pivot: agent-to-agent threats become the primary
feed, conventional threats secondary, so every row needs an explicit
category instead of the frontend inferring one from tags.

Written defensively, like 004: the API also adds this column on cold start
(see app.core.database.ensure_threat_category_column) so production keeps
working between the Vercel deploy and this migration being run, and this
migration skips the column if it already exists.

Backfill heuristic: rows written by the agent pipeline always carry
"surface:" / "propagation:" tags (added by AgentThreatProfile.to_threat_row
and present in the agent seed data), or use a threat_type that only the
agent taxonomy defines. "supply-chain" and "other" exist in both taxonomies,
so they are deliberately absent from the type list.

Revision ID: 005
Revises: 004
"""

import sqlalchemy as sa
from alembic import op

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None

# AGENT_THREAT_TYPES from app.services.ai_service, minus the two values
# shared with the conventional taxonomy ("supply-chain", "other").
AGENT_ONLY_TYPES = (
    "goal-hijack", "prompt-injection", "tool-poisoning", "tool-misuse",
    "identity-spoofing", "privilege-abuse", "code-execution",
    "memory-poisoning", "inter-agent-comms", "cascading-failure",
    "human-trust-exploitation", "rogue-agent", "protocol-vulnerability",
    "framework-vulnerability", "resource-exhaustion", "data-exfiltration",
    "agent-worm",
)

BACKFILL_SQL = """
    UPDATE threats SET category = 'agent'
    WHERE tags ILIKE '%%surface:%%'
       OR tags ILIKE '%%propagation:%%'
       OR threat_type IN ({types})
""".format(types=", ".join(f"'{t}'" for t in AGENT_ONLY_TYPES))


def upgrade():
    bind = op.get_bind()
    columns = [c["name"] for c in sa.inspect(bind).get_columns("threats")]
    if "category" not in columns:
        op.add_column(
            "threats",
            sa.Column("category", sa.String(20), nullable=False,
                      server_default="conventional"),
        )
        op.create_index("ix_threats_category", "threats", ["category"])
    op.execute(BACKFILL_SQL)


def downgrade():
    op.drop_index("ix_threats_category", table_name="threats")
    op.drop_column("threats", "category")
