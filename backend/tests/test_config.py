import json

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_lee_variables_con_prefijo_smd(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SMD_ENVIRONMENT", "ci")
    monkeypatch.setenv("SMD_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("SMD_SECRET_KEY", "valor-sintetico-de-prueba")
    monkeypatch.setenv("SMD_DATABASE_URL", "postgresql://localhost/sintetica")
    s = Settings(_env_file=None)
    assert s.environment == "ci"
    assert s.log_level == "DEBUG"
    assert s.secret_key is not None
    assert s.secret_key.get_secret_value() == "valor-sintetico-de-prueba"
    assert s.database_url is not None
    assert s.database_url.get_secret_value() == "postgresql://localhost/sintetica"


def test_secretos_no_aparecen_en_repr(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SMD_SECRET_KEY", "valor-sintetico-de-prueba")
    monkeypatch.setenv("SMD_DATABASE_URL", "postgresql://localhost/sintetica")
    texto = repr(Settings(_env_file=None))
    assert "valor-sintetico-de-prueba" not in texto
    assert "sintetica" not in texto


def test_variables_sin_prefijo_se_ignoran(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SMD_ENVIRONMENT", raising=False)
    monkeypatch.setenv("APP_ENV", "prod")
    assert Settings(_env_file=None).environment == "dev"


@pytest.mark.parametrize("entorno", ["staging", "prod"])
def test_entornos_estrictos_exigen_secretos(monkeypatch: pytest.MonkeyPatch, entorno: str) -> None:
    monkeypatch.delenv("SMD_SECRET_KEY", raising=False)
    monkeypatch.delenv("SMD_DATABASE_URL", raising=False)
    monkeypatch.setenv("SMD_ENVIRONMENT", entorno)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


# Valores sintéticos, sin credenciales embebidas (el hook secrets_guard veta contraseñas).
SECRETO = "valor-sintetico-secreto-xyz"
URL_BD = "postgresql://host-sintetico/bd-sintetica"
SENSIBLES = (SECRETO, "host-sintetico", "bd-sintetica")


@pytest.mark.parametrize(
    ("entorno", "variable_presente", "valor", "falta"),
    [
        ("prod", "SMD_SECRET_KEY", SECRETO, "SMD_DATABASE_URL"),
        ("staging", "SMD_DATABASE_URL", URL_BD, "SMD_SECRET_KEY"),
    ],
)
def test_error_de_configuracion_no_expone_secretos_en_ninguna_representacion(
    monkeypatch: pytest.MonkeyPatch,
    entorno: str,
    variable_presente: str,
    valor: str,
    falta: str,
) -> None:
    monkeypatch.delenv("SMD_SECRET_KEY", raising=False)
    monkeypatch.delenv("SMD_DATABASE_URL", raising=False)
    monkeypatch.setenv("SMD_ENVIRONMENT", entorno)
    monkeypatch.setenv(variable_presente, valor)
    with pytest.raises(ValidationError) as exc:
        Settings(_env_file=None)
    representaciones = {
        "str": str(exc.value),
        "repr": repr(exc.value),
        "errors": repr(exc.value.errors()),
        "json": exc.value.json(),
    }
    for nombre, texto in representaciones.items():
        for sensible in SENSIBLES:
            assert sensible not in texto, f"{nombre} expone un valor sensible"
        # Diagnosticable: dice qué variable falta, que la configuración es inválida y el entorno.
        assert falta in texto, nombre
    assert "Configuración inválida" in representaciones["str"]
    assert f"'{entorno}'" in representaciones["str"]
    assert "input_value" not in representaciones["str"]


def test_error_sanitizado_no_encadena_la_excepcion_original(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("SMD_DATABASE_URL", raising=False)
    monkeypatch.setenv("SMD_ENVIRONMENT", "prod")
    monkeypatch.setenv("SMD_SECRET_KEY", SECRETO)
    with pytest.raises(ValidationError) as exc:
        Settings(_env_file=None)
    assert exc.value.__cause__ is None
    assert exc.value.__context__ is None


@pytest.mark.parametrize("entorno", ["dev", "ci", "staging", "prod"])
def test_environment_acepta_solo_valores_exactos(
    monkeypatch: pytest.MonkeyPatch, entorno: str
) -> None:
    monkeypatch.setenv("SMD_SECRET_KEY", SECRETO)
    monkeypatch.setenv("SMD_DATABASE_URL", URL_BD)
    monkeypatch.setenv("SMD_ENVIRONMENT", entorno)
    assert Settings(_env_file=None).environment == entorno


@pytest.mark.parametrize("entorno", ["production", "PROD", "prod ", " staging", ""])
def test_environment_invalido_falla_sin_normalizar(
    monkeypatch: pytest.MonkeyPatch, entorno: str
) -> None:
    monkeypatch.setenv("SMD_ENVIRONMENT", entorno)
    with pytest.raises(ValidationError) as exc:
        Settings(_env_file=None)
    assert "environment" in repr(exc.value.errors())


@pytest.mark.parametrize("comodin", ["*", " * ", "*\t"])
def test_cors_rechaza_comodin(monkeypatch: pytest.MonkeyPatch, comodin: str) -> None:
    monkeypatch.setenv("SMD_CORS_ORIGINS", json.dumps([comodin]))
    with pytest.raises(ValidationError) as exc:
        Settings(_env_file=None)
    assert "cors_origins" in repr(exc.value.errors())


def test_cors_rechaza_comodin_mezclado_con_origenes_validos() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, cors_origins=["http://localhost:5173", "*"])


def test_cors_acepta_origen_explicito(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SMD_CORS_ORIGINS", '["http://localhost:5173"]')
    assert Settings(_env_file=None).cors_origins == ["http://localhost:5173"]


def test_cors_acepta_lista_explicita_multiple(monkeypatch: pytest.MonkeyPatch) -> None:
    origenes = ["http://localhost:5173", "https://app.sintetico.example"]
    monkeypatch.setenv("SMD_CORS_ORIGINS", json.dumps(origenes))
    assert Settings(_env_file=None).cors_origins == origenes


def test_dev_arranca_sin_secretos(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SMD_SECRET_KEY", raising=False)
    monkeypatch.delenv("SMD_DATABASE_URL", raising=False)
    monkeypatch.setenv("SMD_ENVIRONMENT", "dev")
    assert Settings(_env_file=None).secret_key is None
