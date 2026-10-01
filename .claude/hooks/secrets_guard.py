#!/usr/bin/env python3
"""secrets_guard.py - hook PreToolUse de SISTEMAMEDIC.

Bloquea escrituras cuyo contenido parezca:
  * una credencial (clave de nube, token, bloque de clave privada, cadena de
    conexion con contrasena), o
  * un dato real de paciente (8 digitos tipo DNI junto a un nombre, en
    tests/fixtures/datos de prueba).

Entrada: JSON de Claude Code por stdin.
Salida:  0 = sin decision; 2 = BLOQUEADO con motivo en stderr.

No sustituye al escaneo de secretos de la CI: es la primera barrera.
"""

import json
import re
import sys

WRITE_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}

CREDENTIAL_PATTERNS = [
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "bloque de clave privada"),
    # Longitud tolerante: una clave con uno o dos caracteres de mas sigue
    # siendo una clave y no debe colarse por el borde del patron.
    (r"\bAKIA[0-9A-Z]{14,24}\b", "clave de acceso de AWS"),
    (r"\bASIA[0-9A-Z]{14,24}\b", "clave temporal de AWS"),
    (r"\bAIza[0-9A-Za-z_\-]{35}\b", "clave de API de Google"),
    (r"\bya29\.[0-9A-Za-z_\-]{20,}", "token OAuth de Google"),
    (r"\bgh[pousr]_[0-9A-Za-z]{30,}\b", "token de GitHub"),
    (r"\bxox[abprs]-[0-9A-Za-z\-]{10,}\b", "token de Slack"),
    (r"\bsk-[A-Za-z0-9]{32,}\b", "clave de API tipo sk-"),
    (r"\bsk-ant-[A-Za-z0-9\-_]{20,}\b", "clave de API de Anthropic"),
    (r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}",
     "JSON Web Token"),
    (r"(?i)\b(postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis|amqp)://"
     r"[^\s:/@]+:[^\s:/@]+@", "cadena de conexion con contrasena"),
]

# Patron generico de baja confianza: aqui SI se descartan los marcadores.
GENERIC_PATTERN = (
    r"(?i)\b(password|passwd|secret|api[_-]?key|token|private[_-]?key)\s*"
    r"[:=]\s*[\"'][^\"'\s$<>{}]{8,}[\"']"
)

# Valores de marcador que NO son secretos.
PLACEHOLDERS = re.compile(
    r"(?i)(xxx+|changeme|placeholder|your[_-]?|example|dummy|redacted|"
    r"<[^>]{1,40}>|\{\{[^}]{1,40}\}\}|\$\{[^}]{1,40}\}|TODO|FIXME|\*{4,})"
)

# Nombre propio en espanol (con tildes y n) seguido o precedido de 8 digitos.
NAME = r"[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,}(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,})+"
DNI = r"(?<!\d)\d{8}(?!\d)"
DNI_NEAR_NAME = [
    re.compile(NAME + r"[^\n]{0,60}" + DNI),
    re.compile(DNI + r"[^\n]{0,60}" + NAME),
]

# Rutas donde el riesgo de datos reales en fixtures es mayor.
DATA_PATHS = re.compile(
    r"(?i)(^|/)(tests?|e2e|fixtures?|seeds?|factories|data|scripts)(/|$)"
)


def collect_content(payload: dict) -> str:
    ti = payload.get("tool_input") or {}
    chunks = []
    for key in ("content", "new_string", "new_source", "text"):
        val = ti.get(key)
        if isinstance(val, str):
            chunks.append(val)
    edits = ti.get("edits")
    if isinstance(edits, list):
        for e in edits:
            if isinstance(e, dict):
                for key in ("new_string", "content"):
                    if isinstance(e.get(key), str):
                        chunks.append(e[key])
    return "\n".join(chunks)


def target_path(payload: dict) -> str:
    ti = payload.get("tool_input") or {}
    for key in ("file_path", "notebook_path", "path"):
        val = ti.get(key)
        if isinstance(val, str):
            return val.replace("\\", "/")
    return ""


def block(reason: str):
    sys.stderr.write("[secrets_guard] BLOQUEADO: " + reason + "\n")
    sys.exit(2)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(payload, dict):
        return 0
    if (payload.get("tool_name") or "") not in WRITE_TOOLS:
        return 0

    content = collect_content(payload)
    if not content.strip():
        return 0

    # Patrones de alta confianza: un marcador como "EXAMPLE" dentro de una clave
    # con forma valida NO la vuelve inocua, asi que no se descarta.
    for pattern, label in CREDENTIAL_PATTERNS:
        if re.search(pattern, content):
            block(
                "el contenido parece contener %s. Los secretos van en variables de "
                "entorno o en el gestor de secretos, nunca en el repositorio." % label
            )

    # Patron generico: aqui si se aceptan marcadores evidentes.
    m = re.search(GENERIC_PATTERN, content)
    if m and not PLACEHOLDERS.search(m.group(0)):
        block(
            "el contenido parece asignar una credencial literal. Usa una variable "
            "de entorno declarada en .env.example."
        )

    path = target_path(payload)
    if DATA_PATHS.search(path) or not path:
        for rx in DNI_NEAR_NAME:
            m = rx.search(content)
            if m:
                block(
                    "el contenido tiene 8 digitos tipo DNI junto a un nombre propio "
                    "(%r) en una ruta de datos o pruebas. Solo se permiten datos "
                    "sinteticos generados por script (docs/TEST_DATA_POLICY.md)."
                    % m.group(0)[:60]
                )

    return 0


if __name__ == "__main__":
    sys.exit(main())
