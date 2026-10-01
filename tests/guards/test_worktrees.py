#!/usr/bin/env python3
"""Pruebas de regresion de path_guard: worktrees, .git y endurecimiento Windows.

Complementa tests/guards/test_guards.py (que no se modifica). Solo biblioteca
estandar. Los casos de worktree usan un repositorio SINTETICO en el directorio
temporal del sistema: nunca se escribe en el .git del repositorio real. El hook
solo recibe JSON simulado; ninguna prueba escribe en las rutas evaluadas.

    0 = permitido (sin decision)
    2 = bloqueado

Uso:  python tests/guards/test_worktrees.py
      python -m tests.guards.test_worktrees
Debe pasar al 100 %. Si una prueba falla, SE CORRIGE EL GUARD, NUNCA EL TEST.
Los casos que requieren symlinks o junctions se marcan [OMITIDA] (sin contar)
si este sistema no permite crearlos.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH_GUARD = ROOT / ".claude" / "hooks" / "path_guard.py"

ALLOW, BLOCK = 0, 2
WINDOWS = os.name == "nt"

WT = "agent-abc123"        # worktree valido principal
WT_OTRO = "agent-def456"   # segundo worktree valido

AGENTES = [
    "medical-architect",
    "clinical-workflow-reviewer",
    "database-architect",
    "backend-engineer",
    "frontend-medical-ux",
    "security-privacy-reviewer",
    "qa-medical",
    "devops-release-engineer",
    "data-migration-reviewer",
    "final-reviewer",
]

_results = []
_skipped = []


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------
def run_hook(payload: dict, args, project_dir: Path):
    return run_raw(json.dumps(payload), args, project_dir)


def run_raw(stdin_text: str, args, project_dir: Path):
    env = dict(os.environ)
    env["CLAUDE_PROJECT_DIR"] = str(project_dir)
    proc = subprocess.run(
        [sys.executable, str(PATH_GUARD)] + list(args),
        input=stdin_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        cwd=str(project_dir),
    )
    return proc.returncode, (proc.stderr or "").strip()


def write_payload(file_path, agent_type=None, tool="Write"):
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": tool,
        "tool_input": {"file_path": file_path, "content": "contenido de prueba"},
    }
    if agent_type:
        payload["agent_type"] = agent_type
    return payload


def check(name, expected, got, detail=""):
    ok = expected == got
    _results.append((ok, name, expected, got, detail))
    mark = "OK  " if ok else "FALLA"
    line = "  [%s] %s" % (mark, name)
    if not ok:
        line += "  (esperado %s, obtenido %s) %s" % (expected, got, detail)
    print(line)


def skip(name, reason):
    _skipped.append((name, reason))
    print("  [OMITIDA] %s (%s)" % (name, reason))


def expect(name, file_path, expected, project_dir, agent_type=None,
           domain="main", tool="Write"):
    code, err = run_hook(write_payload(file_path, agent_type, tool),
                         [domain], project_dir)
    check(name, expected, code, err[:200])


def quien(agente):
    return agente or "main"


def _write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def registrar_worktree(main: Path, wt_dir: Path, admin_name: str):
    """Imita `git worktree add`: archivo .git + carpeta admin con puntero."""
    admin = main / ".git" / "worktrees" / admin_name
    admin.mkdir(parents=True, exist_ok=True)
    wt_dir.mkdir(parents=True, exist_ok=True)
    _write(wt_dir / ".git", "gitdir: %s\n" % admin.as_posix())
    _write(admin / "gitdir", "%s\n" % (wt_dir / ".git").as_posix())
    _write(admin / "commondir", "../..\n")
    return admin


def crear_enlace_dir(link: Path, target: Path):
    """Symlink de directorio o, en Windows, junction. None si no se puede."""
    link.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.symlink(str(target), str(link), target_is_directory=True)
        return "symlink"
    except (OSError, NotImplementedError, AttributeError):
        pass
    if WINDOWS:
        try:
            import _winapi
            _winapi.CreateJunction(str(target), str(link))
            return "junction"
        except Exception:
            pass
    return None


def crear_repo_sintetico():
    main = Path(tempfile.mkdtemp(prefix="smp_guard_")).resolve()
    (main / ".git" / "worktrees").mkdir(parents=True)
    for d in ("backend/app", "frontend/src", "docs"):
        (main / d).mkdir(parents=True, exist_ok=True)
    for name in (WT, WT_OTRO):
        wt = main / ".claude" / "worktrees" / name
        for d in ("backend/app/sub", "frontend/src", "docs", "tests/guards"):
            (wt / d).mkdir(parents=True, exist_ok=True)
        registrar_worktree(main, wt, name)
    return main


def wtp(rel, name=WT):
    return ".claude/worktrees/%s/%s" % (name, rel)


# --------------------------------------------------------------------------
# (l) Dominio dentro de un worktree (CLAUDE_PROJECT_DIR = raiz)
# --------------------------------------------------------------------------
def test_l_dominio_en_worktree(main):
    print("\n(l) Reglas de dominio dentro de un worktree")
    casos = [
        ("backend-engineer", "backend/app/x.py", ALLOW),
        ("backend-engineer", "frontend/src/x.ts", BLOCK),
        ("backend-engineer", "backend/tests/x.py", BLOCK),
        ("backend-engineer", "backend/migrations/x.py", BLOCK),
        ("frontend-medical-ux", "frontend/src/x.ts", ALLOW),
        ("frontend-medical-ux", "backend/app/x.py", BLOCK),
        ("frontend-medical-ux", "frontend/tests/x.ts", BLOCK),
        ("qa-medical", "backend/tests/x.py", ALLOW),
        ("database-architect", "backend/migrations/x.py", ALLOW),
        ("medical-architect", "docs/nota.md", ALLOW),
        ("devops-release-engineer", ".github/workflows/ci.yml", ALLOW),
        ("security-privacy-reviewer", "docs/nota.md", BLOCK),
        (None, "README.md", ALLOW),
    ]
    for agente, rel, esperado in casos:
        expect("%s wt -> %s" % (quien(agente), rel), wtp(rel), esperado,
               main, agent_type=agente)
    absoluta = str(main / ".claude" / "worktrees" / WT / "backend" / "app" / "x.py")
    expect("backend-engineer wt -> backend/app/x.py absoluta", absoluta, ALLOW,
           main, agent_type="backend-engineer")
    absoluta = str(main / ".claude" / "worktrees" / WT / "frontend" / "src" / "x.ts")
    expect("backend-engineer wt -> frontend/src/x.ts absoluta", absoluta, BLOCK,
           main, agent_type="backend-engineer")


# --------------------------------------------------------------------------
# (m) Rutas protegidas dentro de un worktree: bloqueadas para todos
# --------------------------------------------------------------------------
def test_m_protegidas_en_worktree(main):
    print("\n(m) Rutas protegidas dentro del worktree -> BLOQUEADAS para todos")
    protegidas = [
        "docs/APPROVALS.md",
        ".claude/hooks/path_guard.py",
        ".claude/settings.json",
        ".claude/agents/x.md",
        "tests/guards/x.py",
        ".env",
        "backend/.env.local",
        ".git",
        "secrets/x.json",
    ]
    for agente in AGENTES + [None]:
        for rel in protegidas:
            expect("%s wt -> %s" % (quien(agente), rel), wtp(rel), BLOCK,
                   main, agent_type=agente)
    # La plantilla sigue permitida para main (no se endurece de mas).
    expect("main wt -> .env.example", wtp(".env.example"), ALLOW, main)


# --------------------------------------------------------------------------
# (n) Escapes con ..
# --------------------------------------------------------------------------
def test_n_escapes(main):
    print("\n(n) Escapes con '..' que involucran un worktree -> BLOQUEADOS")
    casos = [
        wtp("../../settings.json"),
        wtp("../%s/backend/app/x.py" % WT_OTRO),
        wtp("backend/../backend/app/x.py"),
        wtp("../../../backend/app/x.py"),
        ".claude\\worktrees\\%s\\..\\..\\settings.json" % WT,
        str(main / ".claude" / "worktrees" / WT) + "/../../settings.json",
        "backend/../.claude/worktrees/%s/backend/app/x.py" % WT,
    ]
    for ruta in casos:
        for agente in (None, "backend-engineer"):
            expect("%s -> %s" % (quien(agente), ruta), ruta, BLOCK, main,
                   agent_type=agente)


# --------------------------------------------------------------------------
# (o) Nombres de worktree invalidos y escrituras sobre la carpeta de worktrees
# --------------------------------------------------------------------------
def test_o_nombre_invalido(main):
    print("\n(o) Nombre de worktree invalido -> BLOQUEADO")
    for nombre in ("otro", "agent-xyz", "agent-", "agent-abc123x",
                   "xagent-abc123", "agent_abc123"):
        # Con .git valido: solo falla el nombre.
        wt = main / ".claude" / "worktrees" / nombre
        registrar_worktree(main, wt, "n-" + nombre.replace("_", "-"))
        for agente in (None, "backend-engineer"):
            expect("%s -> worktree %r backend/app/x.py" % (quien(agente), nombre),
                   wtp("backend/app/x.py", nombre), BLOCK, main,
                   agent_type=agente)
    expect("main -> .claude/worktrees/nuevo.txt", ".claude/worktrees/nuevo.txt",
           BLOCK, main)
    expect("main -> carpeta del worktree", ".claude/worktrees/%s" % WT,
           BLOCK, main)
    expect("main -> .claude/worktrees", ".claude/worktrees", BLOCK, main)


# --------------------------------------------------------------------------
# (p) Worktree sin .git
# --------------------------------------------------------------------------
def test_p_sin_git(main):
    print("\n(p) Worktree sin .git -> BLOQUEADO")
    (main / ".claude" / "worktrees" / "agent-0bad00" / "backend" / "app").mkdir(
        parents=True, exist_ok=True)
    for agente in (None, "backend-engineer"):
        expect("%s -> agent-0bad00 sin .git" % quien(agente),
               wtp("backend/app/x.py", "agent-0bad00"), BLOCK, main,
               agent_type=agente)
    expect("backend-engineer -> worktree inexistente agent-0bad99",
           wtp("backend/app/x.py", "agent-0bad99"), BLOCK, main,
           agent_type="backend-engineer")


# --------------------------------------------------------------------------
# (q) Worktree anidado y segmentos .claude/worktrees falsos
# --------------------------------------------------------------------------
def test_q_anidado(main):
    print("\n(q) Worktree anidado o falso -> BLOQUEADO")
    anidado = main / ".claude" / "worktrees" / WT / ".claude" / "worktrees" / "agent-def789"
    registrar_worktree(main, anidado, "agent-def789")
    casos = [
        wtp(".claude/worktrees/agent-def789/backend/app/x.py"),
        wtp(".claude/worktrees/agent-def789/README.md"),
        wtp(".claude/worktrees/agent-123abc/README.md"),
        wtp("backend/.claude/worktrees/agent-def789/x.py"),
        "backend/.claude/worktrees/%s/x.py" % WT,
        "docs/.claude/worktrees/%s/nota.md" % WT,
    ]
    for ruta in casos:
        for agente in (None, "backend-engineer"):
            expect("%s -> %s" % (quien(agente), ruta), ruta, BLOCK, main,
                   agent_type=agente)


# --------------------------------------------------------------------------
# (r) .git del repositorio principal (y de worktrees / repos anidados)
# --------------------------------------------------------------------------
def test_r_git(main):
    print("\n(r) Escrituras en .git -> BLOQUEADAS para todos")
    rutas = [".git", ".git/config", ".git/hooks/pre-commit",
             ".git/worktrees/%s/gitdir" % WT, "backend/.git/config",
             wtp(".git"), wtp("backend/.git/hooks/post-checkout")]
    for ruta in rutas:
        for agente in (None, "devops-release-engineer", "backend-engineer"):
            expect("%s -> %s" % (quien(agente), ruta), ruta, BLOCK, main,
                   agent_type=agente)
    absoluta = str(main / ".git" / "config")
    expect("main -> .git/config absoluta", absoluta, BLOCK, main)
    # En el repositorio REAL (solo se evalua el JSON; no se escribe nada).
    expect("main -> .git/config (repo real)", ".git/config", BLOCK, ROOT)
    expect("main -> .git/hooks/pre-commit (repo real)", ".git/hooks/pre-commit",
           BLOCK, ROOT)
    # No regresion: nombres parecidos siguen permitidos.
    expect("main -> .gitignore", ".gitignore", ALLOW, main)
    expect("main -> .gitattributes", ".gitattributes", ALLOW, main)
    expect("devops -> .github/workflows/ci.yml", ".github/workflows/ci.yml",
           ALLOW, main, agent_type="devops-release-engineer")


# --------------------------------------------------------------------------
# (s) CLAUDE_PROJECT_DIR apuntando al worktree
# --------------------------------------------------------------------------
def test_s_project_dir_worktree(main):
    print("\n(s) CLAUDE_PROJECT_DIR = worktree -> misma decision que en la raiz")
    wt = main / ".claude" / "worktrees" / WT
    casos = [
        ("backend-engineer", "backend/app/x.py", ALLOW),
        ("backend-engineer", "frontend/src/x.ts", BLOCK),
        ("backend-engineer", "backend/tests/x.py", BLOCK),
        ("backend-engineer", "backend/migrations/x.py", BLOCK),
        ("frontend-medical-ux", "frontend/src/x.ts", ALLOW),
        ("frontend-medical-ux", "backend/app/x.py", BLOCK),
        ("security-privacy-reviewer", "docs/nota.md", BLOCK),
        (None, "README.md", ALLOW),
        (None, "docs/APPROVALS.md", BLOCK),
        (None, ".claude/hooks/path_guard.py", BLOCK),
        (None, ".claude/settings.json", BLOCK),
        (None, "tests/guards/x.py", BLOCK),
        (None, ".env", BLOCK),
        (None, ".git", BLOCK),
    ]
    for agente, rel, esperado in casos:
        q = quien(agente)
        expect("%s raiz     -> %s" % (q, rel), rel, esperado, main,
               agent_type=agente)
        expect("%s raiz     -> wt/%s" % (q, rel), wtp(rel), esperado, main,
               agent_type=agente)
        expect("%s env=wt   -> %s" % (q, rel), rel, esperado, wt,
               agent_type=agente)
        expect("%s env=wt   -> absoluta wt/%s" % (q, rel),
               str(wt.joinpath(*rel.split("/"))), esperado, wt,
               agent_type=agente)

    # Absoluta hacia la raiz principal: misma decision que con env=raiz.
    expect("backend-engineer env=wt -> absoluta raiz backend/app/x.py",
           str(main / "backend" / "app" / "x.py"), ALLOW, wt,
           agent_type="backend-engineer")
    expect("main env=wt -> absoluta raiz docs/APPROVALS.md",
           str(main / "docs" / "APPROVALS.md"), BLOCK, wt)
    # '..' con base en worktree: bloqueado.
    expect("backend-engineer env=wt -> ../../../backend/app/x.py",
           "../../../backend/app/x.py", BLOCK, wt,
           agent_type="backend-engineer")
    expect("main env=wt -> ../../settings.json", "../../settings.json",
           BLOCK, wt)

    print("\n(s2) CLAUDE_PROJECT_DIR = worktree sin raiz determinable -> BLOQUEADO")
    base = main / ".claude" / "worktrees"

    sin_git = base / "agent-0bad10"
    sin_git.mkdir(parents=True, exist_ok=True)

    basura = base / "agent-0bad11"
    _write(basura / ".git", "esto no es un gitdir\n")

    admin_inexistente = base / "agent-0bad12"
    _write(admin_inexistente / ".git", "gitdir: %s\n"
           % (main / ".git" / "worktrees" / "no-existe").as_posix())

    puntero_falso = base / "agent-0bad13"
    admin = registrar_worktree(main, puntero_falso, "agent-0bad13")
    _write(admin / "gitdir", "%s\n" % (base / WT / ".git").as_posix())

    fuera_de_worktrees = main / "otros" / "agent-0bad14"
    registrar_worktree(main, fuera_de_worktrees, "agent-0bad14")

    gitdir_no_worktrees = base / "agent-0bad15"
    gitdir_no_worktrees.mkdir(parents=True, exist_ok=True)
    _write(gitdir_no_worktrees / ".git", "gitdir: %s\n"
           % (main / ".git").as_posix())

    nombre_invalido = base / "otro-wt"
    registrar_worktree(main, nombre_invalido, "otro-wt")

    dos_lineas = base / "agent-0bad16"
    admin2 = registrar_worktree(main, dos_lineas, "agent-0bad16")
    _write(dos_lineas / ".git", "gitdir: %s\ngitdir: %s\n"
           % (admin2.as_posix(), admin2.as_posix()))

    anidado = base / WT / ".claude" / "worktrees" / "agent-0bad17"
    registrar_worktree(main, anidado, "agent-0bad17")

    malos = [
        ("worktree sin .git", sin_git),
        (".git con contenido basura", basura),
        ("gitdir inexistente", admin_inexistente),
        ("puntero de vuelta a otro worktree", puntero_falso),
        ("worktree fuera de .claude/worktrees", fuera_de_worktrees),
        ("gitdir que no esta en .git/worktrees", gitdir_no_worktrees),
        ("worktree con nombre invalido", nombre_invalido),
        (".git con dos lineas", dos_lineas),
        ("worktree anidado", anidado),
    ]
    for etiqueta, proyecto in malos:
        expect("main env=%s -> README.md" % etiqueta, "README.md", BLOCK,
               proyecto)
        expect("backend-engineer env=%s -> backend/app/x.py" % etiqueta,
               "backend/app/x.py", BLOCK, proyecto,
               agent_type="backend-engineer")


# --------------------------------------------------------------------------
# (t) Mayusculas/minusculas y separadores Windows dentro de worktrees
# --------------------------------------------------------------------------
def test_t_variantes(main):
    print("\n(t) Variantes de mayusculas y separadores -> misma decision")
    abs_wt = main / ".claude" / "worktrees" / WT
    separadores = [
        ("backend-engineer", wtp("backend/app/x.py"),
         ".claude\\worktrees\\%s\\backend\\app\\x.py" % WT, ALLOW),
        ("backend-engineer", wtp("frontend/src/x.ts"),
         ".claude\\worktrees\\%s\\frontend\\src\\x.ts" % WT, BLOCK),
        (None, wtp("docs/APPROVALS.md"),
         ".claude\\worktrees\\%s\\docs\\APPROVALS.md" % WT, BLOCK),
        (None, wtp(".claude/hooks/path_guard.py"),
         ".claude/worktrees\\%s/.claude\\hooks/path_guard.py" % WT, BLOCK),
        ("backend-engineer", wtp("backend/app/x.py"),
         str(abs_wt / "backend" / "app" / "x.py").replace("/", "\\"), ALLOW),
    ]
    mayusculas = [
        ("backend-engineer", wtp("backend/app/x.py"),
         ".CLAUDE/WORKTREES/AGENT-ABC123/BACKEND/APP/x.py", ALLOW),
        ("backend-engineer", wtp("backend/app/x.py"),
         ".Claude\\Worktrees\\Agent-Abc123\\Backend\\App\\X.PY", ALLOW),
        ("backend-engineer", wtp("backend/tests/x.py"),
         ".CLAUDE\\worktrees\\agent-ABC123\\BACKEND\\TESTS\\x.py", BLOCK),
        ("frontend-medical-ux", wtp("frontend/src/x.ts"),
         ".claude/WORKTREES/agent-abc123/FRONTEND/SRC/X.TS", ALLOW),
        (None, wtp("docs/APPROVALS.md"),
         ".claude/worktrees/AGENT-abc123/DOCS/approvals.md", BLOCK),
        (None, wtp(".claude/hooks/path_guard.py"),
         ".claude\\worktrees\\agent-abc123\\.CLAUDE\\HOOKS\\PATH_GUARD.PY", BLOCK),
        (None, wtp(".claude/settings.json"),
         ".claude/worktrees/agent-abc123/.Claude/Settings.JSON", BLOCK),
        (None, wtp("tests/guards/x.py"),
         ".claude/worktrees/agent-abc123/TESTS/GUARDS/x.py", BLOCK),
        (None, ".git/config", ".GIT\\CONFIG", BLOCK),
        (None, wtp(".git"), ".claude/worktrees/agent-abc123/.GIT", BLOCK),
        ("backend-engineer", wtp("backend/app/x.py"),
         str(abs_wt / "backend" / "app" / "x.py").lower(), ALLOW),
        ("backend-engineer", wtp("backend/app/x.py"),
         str(abs_wt / "backend" / "app" / "x.py").upper(), ALLOW),
    ]
    for agente, canonica, variante, esperado in separadores:
        q = quien(agente)
        expect("%s canonica %s" % (q, canonica), canonica, esperado, main,
               agent_type=agente)
        expect("%s variante %s" % (q, variante), variante, esperado, main,
               agent_type=agente)
    for agente, canonica, variante, esperado in mayusculas:
        q = quien(agente)
        if not WINDOWS:
            skip("%s variante %s" % (q, variante),
                 "mayusculas: sistema de archivos sensible a mayusculas")
            continue
        expect("%s canonica %s" % (q, canonica), canonica, esperado, main,
               agent_type=agente)
        expect("%s variante %s" % (q, variante), variante, esperado, main,
               agent_type=agente)


# --------------------------------------------------------------------------
# (u) Endurecimiento Windows: punto/espacio final, ADS, 8.3, dispositivos
# --------------------------------------------------------------------------
def test_u_windows(main):
    print("\n(u) Formas que Windows reinterpreta -> BLOQUEADAS")
    aprob = str(ROOT / "docs" / "APPROVALS.md")
    bloqueadas_main = [
        # Punto y espacio final
        "docs/APPROVALS.md.",
        "docs/APPROVALS.md ",
        "docs/APPROVALS.md...",
        "docs/APPROVALS.md. .",
        "docs./APPROVALS.md",
        "docs /APPROVALS.md",
        "docs\\APPROVALS.md.",
        ".env.",
        ".env ",
        ".claude/settings.json.",
        ".claude./hooks/path_guard.py",
        ".claude/hooks./path_guard.py",
        "tests/guards./x.py",
        ".git./config",
        "...",
        # Alternate Data Streams y rutas relativas a unidad
        "docs/APPROVALS.md::$DATA",
        "docs/APPROVALS.md:$DATA",
        "docs/APPROVALS.md:oculto",
        "docs/APPROVALS.md:oculto:$DATA",
        "docs\\APPROVALS.md::$DATA",
        "DOCS\\approvals.md::$data",
        ".env::$DATA",
        ".claude/hooks/path_guard.py::$DATA",
        ".claude/settings.json:x",
        "docs::$INDEX_ALLOCATION/APPROVALS.md",
        ".git::$INDEX_ALLOCATION/config",
        "C:docs/APPROVALS.md",
        aprob + "::$DATA",
        aprob + ".",
        # Nombres cortos 8.3
        "DOCS~1/APPROVALS.md",
        "docs/APPROV~1.MD",
        "CLAUDE~1/hooks/path_guard.py",
        ".claude/SETTIN~1.JSO",
        # Nombres de dispositivo
        "docs/CON",
        "docs/nul.md",
        "docs/COM1.txt",
        "docs/LPT1",
        "AUX",
        # Prefijos UNC / dispositivo
        "\\\\?\\" + aprob,
        "\\\\.\\" + aprob,
        "\\\\?\\UNC\\localhost\\c$\\x.md",
        "//localhost/c$/x.md",
        # Comodines
        "docs/APPRO*.md",
        "docs/APPROVALS.m?",
        "docs/<x>.md",
        # Espacios al inicio de la ruta completa
        " docs/APPROVALS.md",
    ]
    for ruta in bloqueadas_main:
        expect("main -> %r" % ruta, ruta, BLOCK, ROOT)

    # Tambien rutas NO protegidas: falla cerrado ante cualquier forma ambigua.
    for ruta in ("docs/nota.md:stream", "docs/nota.md.", "docs/nota.md ",
                 " docs/nota.md", "docs/NOTA~1.MD"):
        expect("docs -> %r" % ruta, ruta, BLOCK, ROOT, domain="docs")

    # Dentro de un worktree.
    for agente, rel in (
            ("backend-engineer", "backend/app/x.py."),
            ("backend-engineer", "backend/app/x.py::$DATA"),
            ("backend-engineer", "backend/app/x.py "),
            ("backend-engineer", "backend/tests./x.py"),
            (None, "docs/APPROVALS.md."),
            (None, "docs/APPROVALS.md::$DATA"),
            (None, ".claude/hooks/path_guard.py."),
    ):
        expect("%s wt -> %r" % (quien(agente), rel), wtp(rel), BLOCK, main,
               agent_type=agente)
    expect("main -> nombre de worktree con punto final",
           ".claude/worktrees/%s./backend/app/x.py" % WT, BLOCK, main)
    expect("main -> nombre de worktree con ADS",
           ".claude/worktrees/%s::$INDEX_ALLOCATION/README.md" % WT, BLOCK, main)

    print("\n(u2) No regresion: nombres legitimos siguen permitidos")
    permitidas = [
        ("docs", "docs/v1.2/nota.md"),
        ("docs", "docs/nota.v2.md"),
        ("docs", "docs/.nota.md"),
        ("docs", "docs/a b/nota.md"),
        ("docs", "./docs/nota.md"),
        ("docs", str(ROOT / "docs" / "NOTA.md")),
        ("main", ".env.example"),
        ("main", "README.md"),
        ("devops", "docker-compose.dev.yml"),
    ]
    for dominio, ruta in permitidas:
        expect("%s -> %r" % (dominio, ruta), ruta, ALLOW, ROOT, domain=dominio)


# --------------------------------------------------------------------------
# (v) Symlinks / junctions
# --------------------------------------------------------------------------
def test_v_enlaces(main, fuera):
    print("\n(v) Symlinks y junctions -> sin escape del worktree")
    wt = main / ".claude" / "worktrees" / WT
    (wt / "backend" / "app" / "sub").mkdir(parents=True, exist_ok=True)
    (fuera / "dir").mkdir(parents=True, exist_ok=True)

    casos = [
        # (nombre, enlace, destino, ruta evaluada, agente, esperado)
        ("wt -> raiz principal", wt / "backend" / "app" / "esc",
         main / "backend" / "app", wtp("backend/app/esc/x.py"),
         "backend-engineer", BLOCK),
        ("wt -> fuera del repo", wt / "backend" / "app" / "fuera",
         fuera / "dir", wtp("backend/app/fuera/x.py"),
         "backend-engineer", BLOCK),
        ("raiz -> wt", main / "backend" / "app" / "hacia_wt",
         wt / "backend" / "app", "backend/app/hacia_wt/x.py",
         "backend-engineer", BLOCK),
        ("wt -> otro worktree", wt / "backend" / "app" / "otro",
         main / ".claude" / "worktrees" / WT_OTRO / "backend" / "app",
         wtp("backend/app/otro/x.py"), "backend-engineer", BLOCK),
        ("carpeta de worktree enlazada a la raiz",
         main / ".claude" / "worktrees" / "agent-fff000", main,
         ".claude/worktrees/agent-fff000/backend/app/x.py", None, BLOCK),
        ("wt docs -> docs de la raiz", wt / "docs" / "enlace",
         main / "docs", wtp("docs/enlace/APPROVALS.md"), None, BLOCK),
        ("wt -> tests/guards del propio wt", wt / "backend" / "app" / "aguards",
         wt / "tests" / "guards", wtp("backend/app/aguards/x.py"),
         "backend-engineer", BLOCK),
        ("raiz docs -> fuera del repo", main / "docs" / "fuera",
         fuera / "dir", "docs/fuera/nota.md", "medical-architect", BLOCK),
        # No regresion: enlace interno al MISMO worktree y dominio.
        ("wt -> carpeta del mismo wt", wt / "backend" / "app" / "interno",
         wt / "backend" / "app" / "sub", wtp("backend/app/interno/x.py"),
         "backend-engineer", ALLOW),
    ]
    for nombre, enlace, destino, ruta, agente, esperado in casos:
        tipo = crear_enlace_dir(enlace, destino)
        etiqueta = "%s: %s -> %s" % (nombre, quien(agente), ruta)
        if tipo is None:
            skip(etiqueta, "no se pudo crear symlink ni junction")
            continue
        expect("%s [%s]" % (etiqueta, tipo), ruta, esperado, main,
               agent_type=agente)


# --------------------------------------------------------------------------
# (w) Revision 2: raiz con "~1", nombres de dispositivo, payload sin ruta,
#     worktree falso con .git invalido
# --------------------------------------------------------------------------
def test_w1_raiz_con_tilde():
    print("\n(w1) Raiz real con '~1' en su nombre -> solo se evalua el tramo bajo la raiz")
    otro = Path(tempfile.mkdtemp(prefix="smp~1_raiz_")).resolve()
    try:
        (otro / ".git" / "worktrees").mkdir(parents=True)
        (otro / "docs").mkdir(parents=True)
        wt = otro / ".claude" / "worktrees" / WT
        (wt / "backend" / "app").mkdir(parents=True)
        registrar_worktree(otro, wt, WT)
        casos = [
            (None, str(otro / "docs" / "nota.md"), ALLOW, otro),
            ("backend-engineer", str(otro / "backend" / "app" / "x.py"), ALLOW, otro),
            (None, "docs/nota.md", ALLOW, otro),
            (None, str(otro / "docs" / "APPROVALS.md"), BLOCK, otro),
            (None, str(otro / "docs" / "NOTA~1.MD"), BLOCK, otro),
            (None, str(otro / "docs" / "nota.md") + ".", BLOCK, otro),
            ("backend-engineer", str(wt / "backend" / "app" / "x.py"), ALLOW, otro),
            ("backend-engineer", "backend/app/x.py", ALLOW, wt),
            ("backend-engineer", str(wt / "backend" / "app" / "x.py"), ALLOW, wt),
        ]
        for agente, ruta, esperado, proyecto in casos:
            expect("%s raiz~1 (env=%s) -> %s" % (quien(agente), proyecto.name, ruta),
                   ruta, esperado, proyecto, agent_type=agente)
        variante = str(otro / "docs" / "nota.md").upper()
        if WINDOWS:
            expect("main raiz~1 -> ruta absoluta en mayusculas", variante, ALLOW,
                   otro)
        else:
            skip("main raiz~1 -> ruta absoluta en mayusculas",
                 "mayusculas: sistema de archivos sensible a mayusculas")
    finally:
        shutil.rmtree(str(otro), ignore_errors=True)


def test_w2_dispositivos(main):
    print("\n(w2) Nombres de dispositivo en el frontend -> BLOQUEADOS")
    for ruta, esperado in (
            ("frontend/src/Con.tsx", BLOCK),
            ("frontend/src/components/con.tsx", BLOCK),
            ("frontend/src/CON.TSX", BLOCK),
            ("frontend/src/Nul.tsx", BLOCK),
            ("frontend/src/Aux.ts", BLOCK),
            ("frontend/src/Console.tsx", ALLOW),
            ("frontend/src/Contacto.tsx", ALLOW),
            ("frontend/src/Auxiliar.tsx", ALLOW),
    ):
        expect("frontend-medical-ux -> %s" % ruta, ruta, esperado, ROOT,
               agent_type="frontend-medical-ux")
    expect("frontend-medical-ux wt -> frontend/src/Con.tsx",
           wtp("frontend/src/Con.tsx"), BLOCK, main,
           agent_type="frontend-medical-ux")


def test_w3_payload_sin_ruta():
    print("\n(w3) Payload de escritura sin ruta o ilegible -> BLOQUEADO")

    def payload(tool, tool_input, agente=None):
        p = {"hook_event_name": "PreToolUse", "tool_name": tool}
        if tool_input is not _SIN_INPUT:
            p["tool_input"] = tool_input
        if agente:
            p["agent_type"] = agente
        return json.dumps(p)

    casos = [
        ("Write sin file_path", payload("Write", {"content": "x"}), BLOCK),
        ("Write sin file_path (backend-engineer)",
         payload("Write", {"content": "x"}, "backend-engineer"), BLOCK),
        ("Edit sin file_path",
         payload("Edit", {"old_string": "a", "new_string": "b"}), BLOCK),
        ("NotebookEdit sin notebook_path", payload("NotebookEdit", {}), BLOCK),
        ("MultiEdit con edits vacio", payload("MultiEdit", {"edits": []}), BLOCK),
        ("Write con file_path vacio",
         payload("Write", {"file_path": "", "content": "x"}), BLOCK),
        ("Write con file_path no texto",
         payload("Write", {"file_path": 123, "content": "x"}), BLOCK),
        ("Write con tool_input texto", payload("Write", "docs/x.md"), BLOCK),
        ("Write sin tool_input", payload("Write", _SIN_INPUT), BLOCK),
        ("JSON ilegible", "{esto no es json", BLOCK),
        ("entrada vacia", "", BLOCK),
        ("JSON que no es objeto", json.dumps(["Write", "docs/x.md"]), BLOCK),
        # No regresion: herramientas que no escriben siguen sin decision.
        ("Read sin ruta", payload("Read", {}), ALLOW),
        ("Bash", payload("Bash", {"command": "git status"}), ALLOW),
    ]
    for nombre, stdin_text, esperado in casos:
        code, err = run_raw(stdin_text, ["main"], ROOT)
        check(nombre, esperado, code, err[:200])


_SIN_INPUT = object()


def test_w4_worktree_falso(main):
    print("\n(w4) Worktree falso con .git invalido -> BLOQUEADO")
    base = main / ".claude" / "worktrees"

    basura = base / "agent-0bad20"
    _write(basura / ".git", "esto no es un gitdir\n")

    ajeno = base / "agent-0bad21"
    _write(ajeno / ".git", "gitdir: %s\n"
           % (main / ".git" / "worktrees" / WT).as_posix())

    otro_repo = Path(tempfile.mkdtemp(prefix="smp_otro_repo_")).resolve()
    (otro_repo / ".git" / "worktrees").mkdir(parents=True)
    de_otro_repo = base / "agent-0bad22"
    registrar_worktree(otro_repo, de_otro_repo, "agent-0bad22")

    git_carpeta = base / "agent-0bad23"
    (git_carpeta / ".git").mkdir(parents=True)

    dos_lineas = base / "agent-0bad24"
    admin = registrar_worktree(main, dos_lineas, "agent-0bad24")
    _write(dos_lineas / ".git", "gitdir: %s\ngitdir: %s\n"
           % (admin.as_posix(), admin.as_posix()))

    try:
        for etiqueta, wt in (
                (".git con contenido basura", basura),
                (".git que apunta al admin de otro worktree", ajeno),
                (".git registrado en otro repositorio", de_otro_repo),
                (".git como carpeta", git_carpeta),
                (".git con dos lineas", dos_lineas),
        ):
            ruta = wtp("backend/app/x.py", wt.name)
            for agente in (None, "backend-engineer"):
                expect("%s -> %s (%s)" % (quien(agente), ruta, etiqueta), ruta,
                       BLOCK, main, agent_type=agente)
    finally:
        shutil.rmtree(str(otro_repo), ignore_errors=True)


def main():
    print("Pruebas de worktrees y endurecimiento - path_guard - SISTEMAMEDIC")
    print("Raiz del proyecto: %s" % ROOT)
    if not PATH_GUARD.exists():
        print("ERROR: falta el hook %s" % PATH_GUARD)
        return 1

    repo = crear_repo_sintetico()
    fuera = Path(tempfile.mkdtemp(prefix="smp_fuera_")).resolve()
    print("Repositorio sintetico: %s" % repo)
    try:
        test_l_dominio_en_worktree(repo)
        test_m_protegidas_en_worktree(repo)
        test_n_escapes(repo)
        test_o_nombre_invalido(repo)
        test_p_sin_git(repo)
        test_q_anidado(repo)
        test_r_git(repo)
        test_s_project_dir_worktree(repo)
        test_t_variantes(repo)
        test_u_windows(repo)
        test_v_enlaces(repo, fuera)
        test_w1_raiz_con_tilde()
        test_w2_dispositivos(repo)
        test_w3_payload_sin_ruta()
        test_w4_worktree_falso(repo)
    finally:
        shutil.rmtree(str(repo), ignore_errors=True)
        shutil.rmtree(str(fuera), ignore_errors=True)

    total = len(_results)
    fallos = [r for r in _results if not r[0]]
    print("\n" + "=" * 70)
    print("RESULTADO: %d/%d pasadas" % (total - len(fallos), total))
    print("OMITIDAS (no contadas): %d" % len(_skipped))
    for name, reason in _skipped:
        print("  - %s: %s" % (name, reason))
    if fallos:
        print("\nFALLAS:")
        for _, name, exp, got, detail in fallos:
            print("  - %s: esperado %s, obtenido %s. %s"
                  % (name, exp, got, detail))
        print("\nCorrige el GUARD, nunca el test.")
        return 1
    print("Todos los casos de worktree y endurecimiento se comportan como deben.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
