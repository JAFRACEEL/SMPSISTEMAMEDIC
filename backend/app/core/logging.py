"""Logging JSON con request_id. Sin PHI: solo campos de una lista blanca."""

import json
import logging
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)

# Únicos campos extra permitidos en el log; todo lo demás se descarta (denegación por defecto).
_ALLOWED_EXTRA = ("method", "route", "status_code", "duration_ms")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get(),
        }
        for key in _ALLOWED_EXTRA:
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        if record.exc_info and record.exc_info[0] is not None:
            # Solo el tipo de excepción: el mensaje o la traza pueden contener PHI.
            payload["exc_type"] = record.exc_info[0].__name__
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level.upper())
