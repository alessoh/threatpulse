from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.api.cron import router as cron_router
from app.core.config import get_settings
from app.core.database import ensure_threat_category_column

settings = get_settings()

# Self-healing schema guard for the agent-first pivot (see the function's
# docstring). Never raises; logs and continues if the database is unreachable.
ensure_threat_category_column()

app = FastAPI(
    title="ThreatPulse API",
    description="AI-Powered Cyber Threat Intelligence Platform",
    version="1.0.0",
)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
)

app.include_router(router, prefix="/api")
app.include_router(cron_router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok", "service": "threatpulse-api"}
