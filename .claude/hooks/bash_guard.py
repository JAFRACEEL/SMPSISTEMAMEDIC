#!/usr/bin/env python3
"""bash_guard.py - hook PreToolUse de SISTEMAMEDIC para comandos de shell.

Uso:  python bash_guard.py <perfil>
Perfiles: reviewer | dev

  reviewer -> SOLO lectura de git (status, diff, log, show) y los escaneres
              listados en scripts/readonly_scanners.txt.
  dev      -> allowlist estricta de desarrollo local.

Entrada: JSON de Claude Code por stdin.
Salida:  0 = sin decision; 2 = BLOQUEADO con motivo en stderr.

RIESGO RESIDUAL DOCUMENTADO: el perfil `dev` permite ejecutar pytest, python -m,
npm run, npx y alembic. Un script lanzado por esas vias puede escribir fuera del
dominio del agente, porque el hook no inspecciona lo que el script hace por dentro.
Compensaciones: rama protegida, revision humana del diff y CI (ver
docs/SETUP_DECISIONS.md).
"""

import json
import os
import re
import sys
from pathlib import Path

SHELL_TOOLS = {"Bash", "PowerShell"}

# Metacaracteres de shell prohibidos en AMBOS perfiles.
FORBIDDEN_TOKENS = [
    ("|", "tuberias"),
    (">", "redireccion de salida"),
    ("<", "redireccion de entrada"),
    (";", "encadenado con ;"),
    ("&", "ejecucion en segundo plano o encadenado"),
    ("`", "sustitucion con comillas invertidas"),
    ("$(", "sustitucion de comandos"),
    ("\n", "saltos de linea"),
    ("\r", "saltos de linea"),
]

# Banderas peligrosas en cualquier posicion (perfil reviewer y git del perfil dev).
DANGEROUS_FLAGS = [
    "--output",
    "--no-index",
    "--exec-path",
    "--git-dir",
    "--work-tree",
    "--ext-diff",
    "--upload-pack",
    "--receive-pack",
]

# Opciones globales de git que ejecutan programas o reubican el repositorio.
# Solo son peligrosas ANTES del subcomando: `git -c core.pager=touch log`.
# `git switch -c rama` es legitimo y no entra aqui.
GIT_GLOBAL_DANGEROUS = re.compile(
    r"^git\s+(-c\b|--exec-path\b|--git-dir\b|--work-tree\b|-C\b|--namespace\b)",
    re.IGNORECASE,
)

REVIEWER_ALLOW = [
    "git status",
    "git diff",
    "git log",
    "git show",
]

DEV_ALLOW = [
    # Pruebas y Python
    "pytest",
    "python -m",
    "python tests/",
    "python scripts/",
    "py -m",
    "py tests/",
    "py scripts/",
    # Node
    "npm run",
    "npm ci",
    "npm install",
    "npx ",
    # Migraciones
    "alembic",
    # Contenedores locales
    "docker compose",
    # Git local
    "git status",
    "git diff",
    "git log",
    "git show",
    "git add",
    "git commit",
    "git switch",
    "git branch",
    "git restore --staged",
    # Lectura inocua
    "git rev-parse",
    "git init",
    # Inspeccion de solo lectura del entorno (sesion principal en Windows)
    "Get-ChildItem",
    "Get-Content",
    "Get-Command",
    "Get-Item",
    "Test-Path",
    "Select-String",
    "New-Item -ItemType Directory",
    "claude --version",
    "claude doctor",
    "claude plugin",
    "git --version",
    "node --version",
    "npm --version",
    "docker --version",
    "python --version",
    "py --version",
]

# Prohibidos siempre en `dev`, aunque empiecen por algo permitido.
DEV_DENY_PATTERNS = [
    r"(^|\s)rm(\s|$)",
    r"(^|\s)rmdir(\s|$)",
    r"(^|\s)del(\s|$)",
    r"(^|\s)erase(\s|$)",
    r"(^|\s)mv(\s|$)",
    r"(^|\s)move(\s|$)",
    r"(^|\s)cp(\s|$)",
    r"(^|\s)copy(\s|$)",
    r"(^|\s)tee(\s|$)",
    r"(^|\s)sed\s+-i",
    r"(^|\s)format(\s|$)",
    r"(^|\s)powershell(\.exe)?(\s|$)",
    r"(^|\s)pwsh(\s|$)",
    r"(^|\s)cmd(\.exe)?\s+/c",
    r"(^|\s)curl(\s|$)",
    r"(^|\s)wget(\s|$)",
    r"Invoke-WebRequest",
    r"Invoke-Expression",
    r"(^|\s)iex(\s|$)",
    r"(^|\s)ssh(\s|$)",
    r"(^|\s)scp(\s|$)",
    r"(^|\s)kubectl(\s|$)",
    r"(^|\s)terraform(\s|$)",
    r"(^|\s)aws(\s|$)",
    r"(^|\s)gcloud(\s|$)",
    r"(^|\s)az(\s|$)",
    r"git\s+push",
    r"git\s+reset\s+--hard",
    r"git\s+clean",
    r"--force",
    r"-f\b.*push",
    r"\bstaging\b",
    r"\bprod\b",
    r"\bproduccion\b",
    r"\bproduction\b",
]


def project_root() -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()


def readonly_scanners():
    f = project_root() / "scripts" / "readonly_scanners.txt"
    try:
        lines = f.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    out = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#"):
            out.append(line)
    return out


def block(reason: str):
    sys.stderr.write("[bash_guard] BLOQUEADO: " + reason + "\n")
    sys.exit(2)


def check_tokens(command: str):
    for token, label in FORBIDDEN_TOKENS:
        if token in command:
            block(
                "el comando usa %s (%r), lo que permite eludir la allowlist. "
                "Ejecuta un solo comando simple." % (label, token)
            )


def check_flags(command: str):
    low = " " + command.lower() + " "
    for flag in DANGEROUS_FLAGS:
        if flag in low:
            block("la bandera %r no esta permitida." % flag.strip())
    if GIT_GLOBAL_DANGEROUS.match(command.strip()):
        block(
            "las opciones globales de git antes del subcomando (-c, -C, "
            "--git-dir, --work-tree, --exec-path, --namespace) permiten ejecutar "
            "programas o salir del repositorio."
        )


def starts_with_any(command: str, prefixes) -> bool:
    low = command.strip().lower()
    for p in prefixes:
        pl = p.lower()
        if low == pl.strip() or low.startswith(pl):
            return True
    return False


def main() -> int:
    profile = sys.argv[1] if len(sys.argv) > 1 else "reviewer"

    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(payload, dict):
        return 0

    if (payload.get("tool_name") or "") not in SHELL_TOOLS:
        return 0

    command = (payload.get("tool_input") or {}).get("command") or ""
    if not command.strip():
        return 0

    check_tokens(command)

    if profile == "reviewer":
        check_flags(command)
        allowed = REVIEWER_ALLOW + readonly_scanners()
        if not starts_with_any(command, allowed):
            block(
                "el perfil `reviewer` es de solo lectura. Permitido: %s. "
                "Recibido: %r" % (", ".join(allowed), command.strip())
            )
        return 0

    if profile == "dev":
        low = command.lower()
        for pattern in DEV_DENY_PATTERNS:
            if re.search(pattern, low):
                block(
                    "el comando coincide con un patron prohibido (%s). No se permiten "
                    "borrados, movimientos, red, nubes, push ni nada contra "
                    "staging/PROD." % pattern
                )
        if command.strip().lower().startswith("git "):
            check_flags(command)
        if not starts_with_any(command, DEV_ALLOW):
            block(
                "el comando no esta en la allowlist del perfil `dev`. Permitido: %s. "
                "Recibido: %r" % (", ".join(DEV_ALLOW), command.strip())
            )
        return 0

    block("perfil desconocido: %r" % profile)
    return 2


if __name__ == "__main__":
    sys.exit(main())
