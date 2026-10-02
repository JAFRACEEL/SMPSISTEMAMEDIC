"""Punto de entrada de la API. Esqueleto: solo salud del servicio."""

import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings, utcnow
from app.core.logging import configure_logging, request_id_var

logger = logging.getLogger("app.access")


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    app = FastAPI(title=settings.app_name, docs_url=None, redoc_url=None, openapi_url=None)

    @app.middleware("http")
    async def request_context(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # El request_id lo genera siempre el servidor: no se acepta del cliente (evita inyección
        # en logs).
        rid = uuid.uuid4().hex
        token = request_id_var.set(rid)
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.error("unhandled_error", extra={"method": request.method})
            # Mensaje genérico al cliente; el detalle técnico no incluye PHI.
            response = Response(
                content='{"detail":"Error interno"}',
                status_code=500,
                media_type="application/json",
            )
        route = request.scope.get("route")
        logger.info(
            "request",
            extra={
                "method": request.method,
                # Plantilla de ruta (sin valores de path params ni query string).
                "route": getattr(route, "path", "unmatched"),
                "status_code": response.status_code,
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            },
        )
        response.headers["X-Request-ID"] = rid
        request_id_var.reset(token)
        return response

    # CORS mínimo para DEV: orígenes explícitos (sin comodín), solo lectura, sin credenciales.
    # En DEV el frontend usa el proxy de Vite (mismo origen); esto cubre el acceso directo.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET"],
        allow_headers=["Accept", "Content-Type"],
        allow_credentials=False,
    )

    # Contrato único: toda la API vive bajo /api.
    api = APIRouter(prefix="/api")

    @api.get("/health")
    async def health() -> dict[str, str]:
        """Liveness: el proceso responde."""
        return {"status": "ok"}

    @api.get("/ready")
    async def ready() -> dict[str, object]:
        """Readiness. Aún sin dependencias reales (BD pendiente): informa su estado."""
        return {
            "status": "ready",
            "checks": {"database": "not_configured"},
            "time_utc": utcnow().isoformat(),
        }

    app.include_router(api)

    return app


app = create_app()
