from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok() -> None:
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
    assert r.headers["content-type"].startswith("application/json")


def test_health_incluye_request_id_generado_por_el_servidor() -> None:
    r = client.get("/api/health", headers={"X-Request-ID": "inyectado"})
    assert r.headers["X-Request-ID"] != "inyectado"


def test_ready_informa_bd_no_configurada() -> None:
    r = client.get("/api/ready")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ready"
    assert body["checks"] == {"database": "not_configured"}


def test_ruta_antigua_health_ya_no_existe() -> None:
    # Regresión P3: un único contrato /api/health.
    assert client.get("/health").status_code == 404
    assert client.get("/ready").status_code == 404
