from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import Settings, get_settings
from app.main import app, create_app

client = TestClient(app)

ORIGEN_DEV = "http://localhost:5173"
ORIGEN_PERSONALIZADO = "https://app.sintetico.example"


@pytest.fixture
def cliente_con_origenes(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """Crea una app con SMD_CORS_ORIGINS personalizado y limpia la caché de Settings al salir."""
    monkeypatch.setenv("SMD_CORS_ORIGINS", f'["{ORIGEN_PERSONALIZADO}"]')
    get_settings.cache_clear()
    try:
        yield TestClient(create_app())
    finally:
        monkeypatch.undo()
        get_settings.cache_clear()


def test_origen_por_defecto_permitido() -> None:
    r = client.get("/api/health", headers={"Origin": ORIGEN_DEV})
    assert r.headers["access-control-allow-origin"] == ORIGEN_DEV


def test_preflight_origen_permitido() -> None:
    r = client.options(
        "/api/health",
        headers={"Origin": ORIGEN_DEV, "Access-Control-Request-Method": "GET"},
    )
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == ORIGEN_DEV
    assert "GET" in r.headers["access-control-allow-methods"]
    assert "access-control-allow-credentials" not in r.headers


def test_origen_no_permitido_no_recibe_cabecera_cors() -> None:
    r = client.get("/api/health", headers={"Origin": "https://sitio-ajeno.example"})
    assert r.status_code == 200
    assert "access-control-allow-origin" not in r.headers


def test_preflight_origen_no_permitido_rechazado() -> None:
    r = client.options(
        "/api/health",
        headers={
            "Origin": "https://sitio-ajeno.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert r.status_code == 400
    assert "access-control-allow-origin" not in r.headers


def test_sin_comodin() -> None:
    r = client.get("/api/health", headers={"Origin": ORIGEN_DEV})
    assert r.headers["access-control-allow-origin"] != "*"


def test_origen_personalizado_permitido(cliente_con_origenes: TestClient) -> None:
    r = cliente_con_origenes.get("/api/health", headers={"Origin": ORIGEN_PERSONALIZADO})
    assert r.headers["access-control-allow-origin"] == ORIGEN_PERSONALIZADO
    pre = cliente_con_origenes.options(
        "/api/health",
        headers={"Origin": ORIGEN_PERSONALIZADO, "Access-Control-Request-Method": "GET"},
    )
    assert pre.status_code == 200
    assert pre.headers["access-control-allow-origin"] == ORIGEN_PERSONALIZADO


def test_origen_por_defecto_bloqueado_si_se_reemplaza_la_lista(
    cliente_con_origenes: TestClient,
) -> None:
    r = cliente_con_origenes.get("/api/health", headers={"Origin": ORIGEN_DEV})
    assert "access-control-allow-origin" not in r.headers


@pytest.mark.parametrize("valor", ["http://localhost:5173", "[http://localhost:5173]", "{"])
def test_cors_json_invalido_falla_de_forma_controlada(
    monkeypatch: pytest.MonkeyPatch, valor: str
) -> None:
    monkeypatch.setenv("SMD_CORS_ORIGINS", valor)
    # Pydantic Settings lanza SettingsError (ValueError) por JSON inválido en campos complejos.
    with pytest.raises((ValueError, ValidationError)) as exc:
        Settings(_env_file=None)
    assert "cors_origins" in str(exc.value).lower()
