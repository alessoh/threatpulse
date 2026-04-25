from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql://localhost/threatpulse"
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    anthropic_api_key: str = ""
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

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    if not s.jwt_secret or s.jwt_secret in ("change-me", "change-this-to-a-random-64-char-string"):
        raise RuntimeError(
            "JWT_SECRET is missing or set to the default value. "
            "Generate one with: openssl rand -hex 32  and put it in your .env file."
        )
    return s
