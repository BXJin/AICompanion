from functools import lru_cache
from os import getenv
from typing import Literal

from pydantic import BaseModel, Field


Environment = Literal["local", "dev", "staging", "production"]


class Settings(BaseModel):
    app_name: str = "AI Companion API"
    app_version: str = "0.1.0"
    environment: Environment = Field(default="local")
    debug: bool = False
    log_level: str = "INFO"
    database_url: str = "sqlite+pysqlite:///./ai_companion_local.db"
    request_id_header: str = "X-Request-ID"
    access_token_ttl_seconds: int = 3600
    refresh_token_ttl_seconds: int = 2592000
    admin_api_token: str = "local-admin-token"
    webhook_shared_secret: str = "local-webhook-secret"


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=getenv("AI_COMPANION_APP_NAME", "AI Companion API"),
        app_version=getenv("AI_COMPANION_APP_VERSION", "0.1.0"),
        environment=getenv("AI_COMPANION_ENV", "local"),  # type: ignore[arg-type]
        debug=getenv("AI_COMPANION_DEBUG", "false").lower() == "true",
        log_level=getenv("AI_COMPANION_LOG_LEVEL", "INFO"),
        database_url=getenv("AI_COMPANION_DATABASE_URL", "sqlite+pysqlite:///./ai_companion_local.db"),
        request_id_header=getenv("AI_COMPANION_REQUEST_ID_HEADER", "X-Request-ID"),
        access_token_ttl_seconds=int(getenv("AI_COMPANION_ACCESS_TOKEN_TTL_SECONDS", "3600")),
        refresh_token_ttl_seconds=int(getenv("AI_COMPANION_REFRESH_TOKEN_TTL_SECONDS", "2592000")),
        admin_api_token=getenv("AI_COMPANION_ADMIN_API_TOKEN", "local-admin-token"),
        webhook_shared_secret=getenv("AI_COMPANION_WEBHOOK_SHARED_SECRET", "local-webhook-secret"),
    )
