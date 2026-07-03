from sqlalchemy import create_engine
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
