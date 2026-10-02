"""Configuración por variables de entorno (prefijo SMD_). Sin secretos en código."""

from datetime import UTC, datetime
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SMD_", env_file=".env", extra="ignore")

    app_name: str = "sistemamedic-backend"
    environment: str = "dev"  # dev | ci | staging | prod
    log_level: str = "INFO"
    # Presentación únicamente; el almacenamiento y los logs son siempre UTC.
    display_timezone: str = "America/Lima"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def utcnow() -> datetime:
    """Momento actual con zona UTC (timestamptz). La conversión a Lima es de presentación."""
    return datetime.now(UTC)
