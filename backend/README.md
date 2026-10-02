# Backend SISTEMAMEDIC (esqueleto)

FastAPI + SQLAlchemy + Alembic + Pydantic. Por ahora solo salud del servicio: sin BD, sin
autenticación, sin modelos ni datos de pacientes.

## Ejecutar (dev)

```
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

- `GET /api/health`: liveness.
- `GET /api/ready`: readiness; la BD figura como `not_configured` hasta que exista.

Toda la API vive bajo `/api`. Las rutas `/health` y `/ready` (sin prefijo) ya no existen.

## Configuración

Variables de entorno con prefijo `SMD_` (`SMD_ENVIRONMENT`, `SMD_LOG_LEVEL`,
`SMD_DATABASE_URL`, `SMD_SECRET_KEY`, `SMD_CORS_ORIGINS`, `SMD_DISPLAY_TIMEZONE`).
`SMD_DATABASE_URL` y `SMD_SECRET_KEY` son `SecretStr`; en `staging` y `prod` el arranque falla
si faltan. Sin secretos en el código. Plantilla para DEV: `infra/env/dev.env.example`.

CORS: solo los orígenes de `SMD_CORS_ORIGINS` (lista JSON; por defecto el servidor de Vite),
solo `GET`, sin credenciales y sin comodín.

## Convenciones

- Tiempo en UTC; America/Lima solo para presentación.
- Logs JSON con `request_id` generado por el servidor. Solo método, plantilla de ruta, estado
  y duración: sin PHI, sin query string, sin valores de parámetros de ruta.
- Calidad: `ruff check .`, `mypy .` y `python -m pytest`.
