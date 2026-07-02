"""
Application settings for ThreatPulse.

Drop-in replacement for backend/app/core/config.py. It fixes a latent bug
that only appears when running the backend outside Docker: the project's own
.env template includes frontend-only variables (the NEXT_PUBLIC_* lines), and
with the pinned pydantic-settings version, any variable in the .env file that
is not declared below raises "Extra inputs are not permitted" at startup.
Setting extra="ignore" tells the loader to skip unrecognized variables, which
is the correct behavior for a shared .env file that serves both the backend
and the frontend.

This version also declares an optional anthropic_model setting, so the Claude
model used by the AI service can be changed by adding ANTHROPIC_MODEL=... to
the .env file. When left empty, the AI service falls back to its built-in
default, so nothing changes unless you opt in.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://localhost/threatpulse"
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    anthropic_api_key: str = ""
    anthropic_model: str = ""
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_pro: str = ""
    stripe_price_enterprise: str = ""
    resend_api_key: str = ""
    email_from: str = "alerts@threatpulse.io"
    frontend_url: str = "http://localhost:3000"
    cors_origins: str = "http://localhost:3000"
    scrape_cisa_interval_hours: int = 1
    scrape_nvd_interval_hours: int = 4
    scrape_vendor_interval_hours: int = 12


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    if not s.jwt_secret or s.jwt_secret in ("change-me", "change-this-to-a-random-64-char-string"):
        raise RuntimeError(
            "JWT_SECRET is missing or set to the default value. "
            "Generate one with: openssl rand -hex 32  and put it in your .env file."
        )
    return s
