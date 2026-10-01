#!/usr/bin/env python3
"""path_guard.py - hook PreToolUse de SISTEMAMEDIC.

Limita las escrituras de cada agente (y de la sesion principal) a su dominio.

Uso:  python path_guard.py <dominio>
Dominios: docs | db | backend | frontend | qa | devops | migration | main | none

Entrada: JSON de Claude Code por stdin.
Salida:  codigo 0 = sin decision (sigue el flujo normal de permisos)
         codigo 2 = BLOQUEADO, con el motivo en stderr.

El hook solo se registra con matcher de escritura (Edit|Write|NotebookEdit|
MultiEdit, en settings.json y en los 10 agentes). Por eso un JSON ilegible, un
payload que no es objeto o una herramienta de escritura sin ruta = BLOQUEADO.
Una herramienta que no escribe sigue sin decision (codigo 0).

Si el JSON trae `agent_type` y ese agente esta en AGENT_DOMAINS, el dominio del
agente MANDA sobre el argumento. Asi el hook global protege aunque los hooks de
frontmatter no se carguen (p. ej. carpeta sin confianza aceptada).

Worktrees (isolation: worktree de Claude Code):
  * Una ruta dentro de <raiz>/.claude/worktrees/agent-<hex>/ (con .git propio)
    se evalua relativa a ese worktree, con las MISMAS reglas de dominio y las
    MISMAS rutas protegidas que en la raiz.
  * Solo se quita un nivel de prefijo. Worktree anidado, nombre invalido,
    worktree sin .git, `..` que involucre un worktree, o diferencia entre la
    ruta lexica (normpath) y la real (realpath) = BLOQUEADO.
  * Si CLAUDE_PROJECT_DIR apunta a un worktree, la raiz real se obtiene de su
    archivo .git (gitdir + puntero de vuelta). Si no se puede determinar con
    certeza = BLOQUEADO.

Endurecimiento Windows (se aplica en todas las plataformas, falla cerrado):
  punto o espacio final en un componente, ':' (Alternate Data Streams),
  nombres de dispositivo (CON, NUL, COM1...), nombres cortos 8.3 (~N),
  comodines, prefijos UNC o de dispositivo (\\\\?\\, \\\\.\\) y espacios al
  inicio o final de la ruta = BLOQUEADO antes de aplicar cualquier regla.
  En rutas absolutas se evalua solo el tramo posterior a la raiz, si la ruta
  empieza exactamente por la raiz real; si no, se evalua la ruta completa.
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
    # Metadatos de git (sus hooks ejecutan codigo): repo principal, archivo
    # .git de cada worktree y cualquier repositorio anidado.
    ".git",
    ".git/**",
    "**/.git",
    "**/.git/**",
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

# Nombre de worktree de Claude Code: agent-<hex>.
WORKTREE_NAME_RX = re.compile(r"^agent-[0-9a-f]+$", re.IGNORECASE)

# --- Endurecimiento Windows -----------------------------------------------

_DRIVE_RX = re.compile(r"^[A-Za-z]:$")
# Nombres de dispositivo: Windows los abre como dispositivo con o sin extension.
_RESERVED_RX = re.compile(
    r"^(con|prn|aux|nul|com[0-9\u00b9\u00b2\u00b3]|lpt[0-9\u00b9\u00b2\u00b3]"
    r"|conin\$|conout\$|clock\$)(\..*)?$",
    re.IGNORECASE,
)
# Nombre corto 8.3 (APPROV~1.MD): alias de otro nombre largo.
_SHORTNAME_RX = re.compile(r"~[0-9]")
# Comodines y caracteres invalidos en nombres de Windows.
_FORBIDDEN_CHARS = set('<>"|?*')


# --- Utilidades -----------------------------------------------------------

def _fold(s: str) -> str:
    return s.lower() if CASE_INSENSITIVE else s


def _same_path(a, b) -> bool:
    return _fold(os.path.normpath(str(a))) == _fold(os.path.normpath(str(b)))


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


def windows_hazard(raw_posix: str):
    """Motivo si la ruta usa una forma que Windows reinterpreta; None si no.

    Se evalua sobre la ruta tal como llega (con / como separador), ANTES de
    resolverla, porque Windows normaliza estas formas hacia otro archivo.
    """
    if any(ord(c) < 32 for c in raw_posix):
        return "contiene caracteres de control"
    if raw_posix.startswith("//"):
        return "usa un prefijo UNC o de dispositivo (\\\\?\\, \\\\.\\, \\\\servidor)"
    parts = raw_posix.split("/")
    for i, comp in enumerate(parts):
        if comp in ("", ".", ".."):
            continue
        if i == 0 and len(parts) > 1 and _DRIVE_RX.match(comp):
            continue  # unidad de una ruta absoluta (C:/...)
        if ":" in comp:
            return ("el componente %r contiene ':' (Alternate Data Stream o "
                    "ruta relativa a unidad)" % comp)
        if comp[-1] in ". ":
            return ("el componente %r termina en punto o espacio; Windows lo "
                    "recorta y apunta a otro archivo" % comp)
        if any(ch in _FORBIDDEN_CHARS for ch in comp):
            return "el componente %r contiene comodines o caracteres invalidos" % comp
        if _RESERVED_RX.match(comp):
            return "el componente %r es un nombre de dispositivo de Windows" % comp
        if _SHORTNAME_RX.search(comp):
            return ("el componente %r parece un nombre corto 8.3 (alias de otro "
                    "nombre)" % comp)
    return None


def _split_nonempty(s: str):
    return [x for x in re.split(r"[\\/]+", s) if x]


def _after_root(raw_posix: str, roots) -> str:
    """Tramo de una ruta ABSOLUTA posterior a la raiz.

    Solo se recorta si los componentes iniciales coinciden exactamente (sin
    mayusculas en Windows) con los de una raiz ya resuelta; se usa la raiz mas
    larga que coincida. Si ninguna coincide (alias 8.3, UNC, otra unidad...),
    se devuelve la ruta completa para evaluarla entera (falla cerrado).
    """
    if raw_posix.startswith("//"):
        return raw_posix
    parts = _split_nonempty(raw_posix)
    best = None
    for root in roots:
        rp = _split_nonempty(os.path.normpath(str(root)))
        if not rp or len(rp) > len(parts):
            continue
        if all(_fold(a) == _fold(b) for a, b in zip(parts, rp)):
            if best is None or len(rp) > best:
                best = len(rp)
    if best is None:
        return raw_posix
    return "/".join(parts[best:])


def _rel_parts(path_str: str, root):
    """Componentes de `path_str` relativos a `root`, [] si es la raiz, None si
    queda fuera. Comparacion sin mayusculas en Windows."""
    a = os.path.normpath(path_str)
    b = os.path.normpath(str(root))
    a_cmp, b_cmp = _fold(a), _fold(b)
    if len(a_cmp) != len(a) or len(b_cmp) != len(b):
        return None  # unicode cuyo plegado cambia la longitud: ambiguo
    if a_cmp == b_cmp:
        return []
    prefix = b_cmp.rstrip("\\/") + os.sep
    if not a_cmp.startswith(prefix):
        return None
    rest = a[len(prefix):]
    return [x for x in re.split(r"[\\/]+", rest) if x]


def _is_wt_prefix(parts, i=0) -> bool:
    """parts[i:i+2] == ['.claude', 'worktrees'] (sin mayusculas, siempre)."""
    return (len(parts) >= i + 2 and parts[i].lower() == ".claude"
            and parts[i + 1].lower() == "worktrees")


def _has_wt_segment(parts) -> bool:
    return any(_is_wt_prefix(parts, i) for i in range(len(parts)))


def _read_single_line(path: Path):
    try:
        text = path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError, ValueError):
        return None
    lines = text.splitlines()
    if len(lines) != 1:
        return None
    return lines[0].strip()


def main_root_from_worktree(wt: Path):
    """Raiz del repo principal a partir del archivo .git de un worktree.

    Exige: `gitdir: <raiz>/.git/worktrees/<n>` existente, que <raiz>/.git sea
    carpeta, que el puntero de vuelta <admin>/gitdir apunte a este mismo
    worktree, y que el worktree este en <raiz>/.claude/worktrees/agent-<hex>.
    Cualquier fallo = None (el llamador bloquea).
    """
    line = _read_single_line(wt / ".git")
    if not line or line[:7].lower() != "gitdir:":
        return None
    gitdir = Path(line[7:].strip())
    if not gitdir.is_absolute():
        gitdir = wt / gitdir
    try:
        admin = gitdir.resolve(strict=True)
    except (OSError, RuntimeError, ValueError):
        return None
    if not admin.is_dir():
        return None
    if (admin.parent.name.lower() != "worktrees"
            or admin.parent.parent.name.lower() != ".git"):
        return None
    main_root = admin.parent.parent.parent
    if not (main_root / ".git").is_dir():
        return None

    back = _read_single_line(admin / "gitdir")
    if not back:
        return None
    back_p = Path(back)
    if not back_p.is_absolute():
        back_p = admin / back_p
    try:
        back_p = back_p.resolve(strict=True)
    except (OSError, RuntimeError, ValueError):
        return None
    if not _same_path(back_p, wt / ".git"):
        return None

    parts = _rel_parts(str(wt), main_root)
    if (parts is None or len(parts) != 3 or not _is_wt_prefix(parts, 0)
            or not WORKTREE_NAME_RX.match(parts[2])):
        return None
    return main_root


def repo_context():
    """(raiz_principal, base_para_relativas, base_es_worktree) o None."""
    raw = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    try:
        base = Path(raw).resolve()
    except (OSError, RuntimeError, ValueError):
        return None
    git = base / ".git"
    if git.is_file():
        main_root = main_root_from_worktree(base)
        if main_root is None:
            return None
        return main_root, base, True
    if _has_wt_segment(base.parts):
        # Dentro de .claude/worktrees pero sin archivo .git valido.
        return None
    return base, base, False


def classify(parts, main_root: Path):
    """('main', rel) | ('wt', nombre, rel) | ('bad', motivo)."""
    if _is_wt_prefix(parts, 0):
        if len(parts) < 4:
            return ("bad", "no se escribe sobre .claude/worktrees ni sobre la "
                           "carpeta de un worktree")
        name = parts[2]
        if not WORKTREE_NAME_RX.match(name):
            return ("bad", "%r no es un nombre de worktree valido (agent-<hex>)"
                    % name)
        wt_dir = main_root.joinpath(*parts[:3])
        wt_main = main_root_from_worktree(wt_dir)
        if wt_main is None or not _same_path(wt_main, main_root):
            return ("bad", "el worktree %r no tiene un archivo .git valido que "
                           "apunte a este repositorio (no es un worktree real)"
                    % name)
        inner = parts[3:]
        if _has_wt_segment(inner):
            return ("bad", "worktree anidado dentro de %r" % name)
        return ("wt", name, "/".join(inner))
    if _has_wt_segment(parts):
        return ("bad", "segmento .claude/worktrees fuera de la raiz (worktree "
                       "falso o anidado)")
    return ("main", "/".join(parts))


def effective_rel(target, ctx):
    """(rel_efectiva, rel_completa, worktree, error).

    rel_efectiva: ruta POSIX relativa a la raiz o al worktree, sobre la que se
    aplican las reglas. error != None = bloquear.
    """
    main_root, base, base_is_wt = ctx
    if not isinstance(target, str) or not target:
        return None, None, None, "ruta vacia"
    if target != target.strip():
        return None, None, None, ("%r tiene espacios al inicio o al final"
                                  % target)
    raw = target.strip('"').strip("'").replace("\\", "/")
    if not raw:
        return None, None, None, "ruta vacia"

    # Las formas peligrosas se buscan solo en el tramo bajo la raiz: la raiz
    # real puede llevar legitimamente un "~1" u otro nombre que aqui se
    # rechazaria. Rutas relativas: se evaluan completas.
    tramo = raw
    if Path(raw).is_absolute():
        tramo = _after_root(raw, (base, main_root))
    hazard = windows_hazard(tramo)
    if hazard:
        return None, None, None, "%r %s" % (target, hazard)

    raw_parts = [x for x in raw.split("/") if x]
    if ".." in raw_parts and (
            base_is_wt or any(x.lower() == "worktrees" for x in raw_parts)):
        return None, None, None, ("%r usa '..' en una ruta que involucra un "
                                  "worktree" % target)

    p = Path(raw)
    if not p.is_absolute():
        p = base / p
    lexical = os.path.normpath(str(p))
    # resolve(strict=False): sigue symlinks y junctions existentes.
    try:
        resolved = p.resolve()
    except (OSError, RuntimeError, ValueError):
        return None, None, None, "%r no se pudo resolver" % target

    res_parts = _rel_parts(str(resolved), main_root)
    if res_parts is None:
        return None, None, None, (
            "%r esta fuera del repositorio (%s). Ninguna escritura fuera de la "
            "raiz del proyecto esta permitida." % (target, main_root))
    if not res_parts:
        return None, None, None, "no se puede escribir sobre la raiz del repositorio"
    res = classify(res_parts, main_root)
    if res[0] == "bad":
        return None, None, None, "%r: %s" % (target, res[1])

    lex_parts = _rel_parts(lexical, main_root)
    if lex_parts is None:
        lex = ("outside",)
    elif not lex_parts:
        lex = ("main", "")
    else:
        lex = classify(lex_parts, main_root)
    if lex[0] == "bad":
        return None, None, None, "%r: %s" % (target, lex[1])

    # normpath vs realpath: un symlink o junction no puede meter ni sacar la
    # escritura de un worktree, ni cambiarla de worktree.
    if res[0] == "wt" or lex[0] == "wt":
        if not (res[0] == "wt" and lex[0] == "wt"
                and _fold(res[1]) == _fold(lex[1])):
            return None, None, None, (
                "%r: la ruta real (realpath) no coincide con la ruta escrita "
                "(normpath) respecto a los worktrees; posible symlink o "
                "junction" % target)

    wt_name = res[1] if res[0] == "wt" else None
    return res[-1], "/".join(res_parts), wt_name, None


def targets_from(payload: dict):
    """Rutas que la llamada intenta escribir."""
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return []
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

    # El matcher del hook es solo de escritura: sin JSON legible no se puede
    # saber que se escribe, asi que falla cerrado.
    try:
        payload = json.load(sys.stdin)
    except Exception:
        block("entrada JSON ilegible; no se puede verificar la escritura.")
    if not isinstance(payload, dict):
        block("la entrada JSON no es un objeto; no se puede verificar la escritura.")

    tool_name = payload.get("tool_name") or ""
    if tool_name not in WRITE_TOOLS:
        return 0

    # El dominio del agente manda sobre el argumento.
    agent_type = payload.get("agent_type") or ""
    domain = AGENT_DOMAINS.get(agent_type, arg_domain)
    if domain not in DOMAIN_ALLOW:
        block("dominio desconocido: %r" % domain)

    paths = targets_from(payload)
    if not paths:
        block(
            "%s sin ruta de destino reconocible (file_path/notebook_path/path); "
            "no se puede verificar la escritura." % tool_name
        )

    ctx = repo_context()
    if ctx is None:
        block(
            "no se pudo determinar con certeza la raiz del repositorio principal "
            "(CLAUDE_PROJECT_DIR apunta a un worktree invalido o ambiguo)."
        )

    for raw in paths:
        rel, full, wt_name, err = effective_rel(raw, ctx)
        if err:
            block(err)
        donde = " (worktree %s)" % wt_name if wt_name else ""

        for cand in (rel, full):
            if matches(PROTECTED_ALL, cand) and not matches(
                PROTECTED_EXCEPTIONS, cand
            ):
                block(
                    "%s%s es una ruta protegida para TODOS los agentes y para la "
                    "sesion principal (aprobaciones, secretos, guardrails, .git o "
                    "datos reales). Reportalo, no lo edites." % (rel, donde)
                )

        if domain == "none":
            block(
                "el agente %r es de solo lectura: no puede escribir %s%s. Reporta "
                "el hallazgo en lugar de corregirlo."
                % (agent_type or arg_domain, rel, donde)
            )

        if matches(DOMAIN_DENY.get(domain, []), rel):
            block(
                "%s%s esta excluido del dominio %r (pertenece a otro agente)."
                % (rel, donde, domain)
            )

        if not matches(DOMAIN_ALLOW[domain], rel):
            allowed = ", ".join(DOMAIN_ALLOW[domain]) or "(ninguna)"
            block(
                "%s%s esta fuera del dominio %r. Rutas permitidas: %s"
                % (rel, donde, domain, allowed)
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
