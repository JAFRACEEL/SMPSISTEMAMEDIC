"""Configuración por variables de entorno (prefijo SMD_). Sin secretos en código."""

from datetime import UTC, datetime
from functools import lru_cache
from typing import Any, Literal, Self

from pydantic import SecretStr, ValidationError, field_validator, model_validator
from pydantic_core import InitErrorDetails, PydanticCustomError
from pydantic_settings import BaseSettings, SettingsConfigDict

# Entornos donde el secreto y la BD no pueden faltar (falla cerrada al arrancar).
_ENTORNOS_ESTRICTOS = {"staging", "prod"}


class Settings(BaseSettings):
    # hide_input_in_errors: un ValidationError no debe incluir input_value (SecretStr no lo
    # evita: el validador de modelo recibe todo el diccionario de entrada, secretos incluidos).
    model_config = SettingsConfigDict(
        env_prefix="SMD_", env_file=".env", extra="ignore", hide_input_in_errors=True
    )

    app_name: str = "sistemamedic-backend"
    # Valores exactos: no se normaliza (PROD, "prod " o "production" fallan al arrancar).
    environment: Literal["dev", "ci", "staging", "prod"] = "dev"
    log_level: str = "INFO"
    # Presentación únicamente; el almacenamiento y los logs son siempre UTC.
    display_timezone: str = "America/Lima"
    # Secretos: SecretStr evita que aparezcan en repr, logs o trazas.
    secret_key: SecretStr | None = None
    database_url: SecretStr | None = None
    # Orígenes permitidos por CORS (lista JSON en SMD_CORS_ORIGINS). Sin comodín.
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    def __init__(self, **values: Any) -> None:
        # hide_input_in_errors solo protege str(exc); errors() y json() conservan el input
        # original (con los secretos). Se reconstruye el error sin input ni contexto antes
        # de propagarlo. El raise va fuera del except para no encadenar la excepción original.
        sanitizado: ValidationError | None = None
        try:
            super().__init__(**values)
        except ValidationError as exc:
            sanitizado = _sanitizar_error(exc)
        if sanitizado is not None:
            raise sanitizado

    @field_validator("cors_origins")
    @classmethod
    def _rechazar_comodin_cors(cls, origenes: list[str]) -> list[str]:
        if any(origen.strip() == "*" for origen in origenes):
            raise ValueError("cors_origins no admite el comodín '*'; use orígenes explícitos")
        return origenes

    @model_validator(mode="after")
    def _exigir_secretos_en_entornos_estrictos(self) -> Self:
        if self.environment in _ENTORNOS_ESTRICTOS:
            faltantes = [
                nombre
                for nombre, valor in (
                    ("SMD_SECRET_KEY", self.secret_key),
                    ("SMD_DATABASE_URL", self.database_url),
                )
                if valor is None or not valor.get_secret_value()
            ]
            if faltantes:
                raise ValueError(
                    f"Configuración inválida: faltan variables obligatorias "
                    f"({', '.join(faltantes)}) en el entorno '{self.environment}'"
                )
        return self


def _sanitizar_error(exc: ValidationError) -> ValidationError:
    """Copia del error con loc y mensaje, sin input, contexto ni URL (pueden tener secretos)."""
    lineas: list[InitErrorDetails] = [
        {
            "type": PydanticCustomError(
                "configuracion_invalida", "{mensaje}", {"mensaje": e["msg"]}
            ),
            "loc": e["loc"],
            "input": "<oculto>",
        }
        for e in exc.errors(include_url=False, include_context=False, include_input=False)
    ]
    return ValidationError.from_exception_data(exc.title, lineas, hide_input=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()


def utcnow() -> datetime:
    """Momento actual con zona UTC (timestamptz). La conversión a Lima es de presentación."""
    return datetime.now(UTC)
