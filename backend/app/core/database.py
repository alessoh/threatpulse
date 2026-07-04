from sqlalchemy import create_engine, inspect, text
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import get_settings


def _normalized_url() -> str:
    # Some managed Postgres providers hand out postgres:// URLs, which
    # SQLAlchemy 2.x no longer accepts.
    url = get_settings().database_url
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


# NullPool: on serverless every invocation may be a fresh process, so holding
# a connection pool open only leaks connections. Point DATABASE_URL at your
# provider's *pooled* connection string (PgBouncer/Neon pooler) in production.
engine = create_engine(_normalized_url(), poolclass=NullPool)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_threat_category_column() -> None:
    """Add threats.category if the live database predates migration 005.

    Vercel deploys on merge while migrations run manually from the owner's
    machine, so without this guard every Threat SELECT would 500 between the
    deploy and the migration. Mirrors the defensive daily_insights pattern:
    one catalog inspection per cold start, DDL + backfill only on the first
    start against an old schema. Migration 005 remains the canonical change.
    """
    try:
        if "category" in {c["name"] for c in inspect(engine).get_columns("threats")}:
            return
    except Exception as exc:
        print(f"[schema] category-column inspection skipped: {exc}")
        return
    try:
        from app.services.ai_service import AGENT_THREAT_TYPES

        agent_only = [t for t in AGENT_THREAT_TYPES if t not in ("supply-chain", "other")]
        types_sql = ", ".join(f"'{t}'" for t in agent_only)
        with engine.begin() as conn:
            conn.execute(text(
                "ALTER TABLE threats ADD COLUMN IF NOT EXISTS "
                "category VARCHAR(20) NOT NULL DEFAULT 'conventional'"
            ))
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS ix_threats_category ON threats (category)"
            ))
            conn.execute(text(
                "UPDATE threats SET category = 'agent' "
                "WHERE tags ILIKE '%surface:%' OR tags ILIKE '%propagation:%' "
                f"OR threat_type IN ({types_sql})"
            ))
        print("[schema] added threats.category and backfilled agent rows")
    except Exception as exc:
        print(f"[schema] category-column ensure failed: {exc}")
