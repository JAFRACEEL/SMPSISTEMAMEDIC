#!/usr/bin/env python3
"""path_guard.py - hook PreToolUse de SISTEMAMEDIC.

Limita las escrituras de cada agente (y de la sesion principal) a su dominio.

Uso:  python path_guard.py <dominio>
Dominios: docs | db | backend | frontend | qa | devops | migration | main | none

Entrada: JSON de Claude Code por stdin.
Salida:  codigo 0 = sin decision (sigue el flujo normal de permisos)
         codigo 2 = BLOQUEADO, con el motivo en stderr.

Si el JSON trae `agent_type` y ese agente esta en AGENT_DOMAINS, el dominio del
agente MANDA sobre el argumento. Asi el hook global protege aunque los hooks de
frontmatter no se carguen (p. ej. carpeta sin confianza aceptada).
"""

import json
import os
import re
import sys
from pathlib import Path

# --- Dominios -------------------------------------------------------------

# Patrones permitidos (glob relativo a la raiz del repositorio, con / como separador).
DOMAIN_ALLOW = {
    "docs": ["docs/**"],
    "db": [
        "backend/migrations/**",
        "backend/app/db/**",
        "docs/DATABASE_SCHEMA.md",
    ],
    "backend": ["backend/**"],
    "frontend": ["frontend/src/**", "frontend/public/**"],
    "qa": [
        "backend/tests/**",
        "frontend/tests/**",
        "e2e/**",
        "tests/**",
    ],
    "devops": [
        "infra/**",
        ".github/**",
        "scripts/**",
        "docker-compose*.yml",
        "docker-compose*.yaml",
        "Dockerfile*",
        "*/Dockerfile*",
    ],
    "migration": [
        "docs/DATA_MIGRATION_PLAN.md",
        "scripts/migration/**",
    ],
    "main": ["**"],
    "none": [],
}

# Excepciones dentro del propio dominio.
DOMAIN_DENY = {
    "docs": [],
    "db": [],
    "backend": ["backend/migrations/**", "backend/tests/**"],
    "frontend": [],
    "qa": ["tests/guards/**"],
    "devops": ["scripts/migration/**"],
    "migration": [],
    "main": [],
    "none": [],
}

# Protegido para TODOS los dominios, incluido `main`.
PROTECTED_ALL = [
    "docs/APPROVALS.md",
    ".env",
    ".env.*",
    "**/.env",
    "**/.env.*",
    "**/*.pem",
    "**/*.key",
    "**/*.pfx",
    "**/*.p12",
    "secrets/**",
    "**/secrets/**",
    "data/real/**",
    # Bloqueo final S10: la propia configuracion de los guardrails.
    # Para levantarlo, una PERSONA edita estos archivos fuera de Claude Code
    # (ver docs/SETUP_DECISIONS.md seccion 6).
    ".claude/settings.json",
    ".claude/hooks/**",
    ".claude/agents/**",
    "tests/guards/**",
]

# Excepciones a PROTECTED_ALL: plantillas sin valores.
PROTECTED_EXCEPTIONS = [
    ".env.example",
    "**/.env.example",
]

# Agente -> dominio. Fuente de verdad para el hook global.
AGENT_DOMAINS = {
    "medical-architect": "docs",
    "clinical-workflow-reviewer": "none",
    "database-architect": "db",
    "backend-engineer": "backend",
    "frontend-medical-ux": "frontend",
    "security-privacy-reviewer": "none",
    "qa-medical": "qa",
    "devops-release-engineer": "devops",
    "data-migration-reviewer": "migration",
    "final-reviewer": "none",
}

WRITE_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}

CASE_INSENSITIVE = os.name == "nt"


# --- Utilidades -----------------------------------------------------------

def project_root() -> Path:
    raw = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    return Path(raw).resolve()


def glob_to_regex(pattern: str) -> re.Pattern:
    """Traduce un glob (con ** y *) a regex sobre una ruta POSIX relativa."""
    out = []
    i = 0
    n = len(pattern)
    while i < n:
        ch = pattern[i]
        if ch == "*":
            if pattern.startswith("**/", i):
                # **/ = cero o mas directorios
                out.append("(?:.*/)?")
                i += 3
                continue
            if pattern.startswith("**", i):
                out.append(".*")
                i += 2
                continue
            out.append("[^/]*")
            i += 1
            continue
        if ch == "?":
            out.append("[^/]")
            i += 1
            continue
        out.append(re.escape(ch))
        i += 1
    flags = re.IGNORECASE if CASE_INSENSITIVE else 0
    return re.compile("^" + "".join(out) + "$", flags)


_REGEX_CACHE: dict = {}


def matches(patterns, rel_posix: str) -> bool:
    for pat in patterns:
        rx = _REGEX_CACHE.get(pat)
        if rx is None:
            rx = glob_to_regex(pat)
            _REGEX_CACHE[pat] = rx
        if rx.match(rel_posix):
            return True
    return False


def normalize(target: str, root: Path):
    """Devuelve la ruta relativa POSIX dentro del repo, o None si queda fuera.

    Resuelve `..`, rutas absolutas, separadores de Windows y symlinks.
    """
    if not target:
        return None
    raw = str(target).strip().strip('"').strip("'")
    raw = raw.replace("\\", "/")
    p = Path(raw)
    if not p.is_absolute():
        p = root / p
    # resolve(strict=False) normaliza .. y sigue symlinks si existen.
    try:
        resolved = p.resolve()
    except (OSError, RuntimeError):
        return None
    try:
        root_resolved = root.resolve()
    except (OSError, RuntimeError):
        root_resolved = root

    a = str(resolved)
    b = str(root_resolved)
    if CASE_INSENSITIVE:
        a_cmp, b_cmp = a.lower(), b.lower()
    else:
        a_cmp, b_cmp = a, b
    if a_cmp == b_cmp:
        return ""
    sep = os.sep
    if not a_cmp.startswith(b_cmp.rstrip(sep) + sep):
        return None  # fuera del repositorio
    rel = a[len(b.rstrip(sep)) + 1:]
    return rel.replace("\\", "/")


def targets_from(payload: dict):
    """Rutas que la llamada intenta escribir."""
    tool_input = payload.get("tool_input") or {}
    found = []
    for key in ("file_path", "notebook_path", "path"):
        val = tool_input.get(key)
        if isinstance(val, str) and val:
            found.append(val)
    # MultiEdit / Edit por lotes
    edits = tool_input.get("edits")
    if isinstance(edits, list):
        for e in edits:
            if isinstance(e, dict) and isinstance(e.get("file_path"), str):
                found.append(e["file_path"])
    return found


def block(reason: str):
    sys.stderr.write("[path_guard] BLOQUEADO: " + reason + "\n")
    sys.exit(2)


# --- Principal ------------------------------------------------------------

def main() -> int:
    arg_domain = sys.argv[1] if len(sys.argv) > 1 else "none"

    try:
        payload = json.load(sys.stdin)
    except Exception:
        # Sin JSON legible no hay nada que decidir; no bloquea el flujo normal.
        return 0
    if not isinstance(payload, dict):
        return 0

    tool_name = payload.get("tool_name") or ""
    if tool_name not in WRITE_TOOLS:
        return 0

    # El dominio del agente manda sobre el argumento.
    agent_type = payload.get("agent_type") or ""
    domain = AGENT_DOMAINS.get(agent_type, arg_domain)
    if domain not in DOMAIN_ALLOW:
        block("dominio desconocido: %r" % domain)

    root = project_root()
    paths = targets_from(payload)
    if not paths:
        return 0

    for raw in paths:
        rel = normalize(raw, root)
        if rel is None:
            block(
                "%r esta fuera del repositorio (%s). Ninguna escritura fuera de la "
                "raiz del proyecto esta permitida." % (raw, root)
            )
        if rel == "":
            block("no se puede escribir sobre la raiz del repositorio")

        if matches(PROTECTED_ALL, rel) and not matches(
            PROTECTED_EXCEPTIONS, rel
        ):
            block(
                "%s es una ruta protegida para TODOS los agentes y para la sesion "
                "principal (aprobaciones, secretos o datos reales). Reportalo, no lo "
                "edites." % rel
            )

        if domain == "none":
            block(
                "el agente %r es de solo lectura: no puede escribir %s. Reporta el "
                "hallazgo en lugar de corregirlo." % (agent_type or arg_domain, rel)
            )

        if matches(DOMAIN_DENY.get(domain, []), rel):
            block(
                "%s esta excluido del dominio %r (pertenece a otro agente)."
                % (rel, domain)
            )

        if not matches(DOMAIN_ALLOW[domain], rel):
            allowed = ", ".join(DOMAIN_ALLOW[domain]) or "(ninguna)"
            block(
                "%s esta fuera del dominio %r. Rutas permitidas: %s"
                % (rel, domain, allowed)
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
