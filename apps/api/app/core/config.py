"""Application settings, loaded from the environment only.

Nothing here has a production-ready default: a missing DATABASE_URL should fail
loudly at boot instead of silently pointing at the wrong database.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: Literal["development", "test", "staging", "production"] = "development"
    app_name: str = "Cosmic Signs API"
    api_prefix: str = "/api/v1"
    debug: bool = False
    log_level: str = "INFO"

    database_url: str = Field(
        default="postgresql+asyncpg://cosmic:cosmic@localhost:5436/cosmic_signs",
        description="SQLAlchemy async DSN",
    )
    redis_url: str | None = None

    # Kept as a raw string: pydantic-settings would try to JSON-decode a list
    # field coming from a .env file, which a comma-separated value is not.
    cors_origins: str = "http://localhost:3100"

    # FRAME = only verified calculations, PREVIEW = frame + provisional major stars.
    chart_engine_stage: Literal["FRAME", "PREVIEW"] = "PREVIEW"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def sync_database_url(self) -> str:
        """Alembic runs its migrations synchronously."""
        return self.database_url.replace("+asyncpg", "").replace("+aiosqlite", "")


@lru_cache
def get_settings() -> Settings:
    return Settings()
