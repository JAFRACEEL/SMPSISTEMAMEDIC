# Backend SISTEMAMEDIC (esqueleto)

FastAPI + SQLAlchemy + Alembic + Pydantic. Por ahora solo salud del servicio: sin BD, sin
autenticación, sin modelos ni datos de pacientes.

## Ejecutar (dev)

```
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

- `GET /health`: liveness.
- `GET /ready`: readiness; la BD figura como `not_configured` hasta que exista.

## Configuración

Variables de entorno con prefijo `SMD_` (`SMD_ENVIRONMENT`, `SMD_LOG_LEVEL`,
`SMD_DISPLAY_TIMEZONE`). Sin secretos en el código.

## Convenciones

- Tiempo en UTC; America/Lima solo para presentación.
- Logs JSON con `request_id` generado por el servidor. Solo método, plantilla de ruta, estado
  y duración: sin PHI, sin query string, sin valores de parámetros de ruta.
- Calidad: `ruff check .` y `mypy app`.
