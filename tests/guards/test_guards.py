#!/usr/bin/env python3
"""Pruebas de violacion de los guardrails de SISTEMAMEDIC.

Solo biblioteca estandar. Alimentan los hooks de .claude/hooks/ con JSON
simulado por stdin y verifican el codigo de salida.

    0 = permitido (sin decision)
    2 = bloqueado

Uso:  python tests/guards/test_guards.py
Debe pasar al 100 %. Si una prueba falla, SE CORRIGE EL GUARD, NUNCA EL TEST.
"""

import contextlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOKS = ROOT / ".claude" / "hooks"
PATH_GUARD = HOOKS / "path_guard.py"
BASH_GUARD = HOOKS / "bash_guard.py"
SECRETS_GUARD = HOOKS / "secrets_guard.py"

ALLOW, BLOCK = 0, 2

_results = []


def run_hook(script: Path, args, payload: dict):
    env = dict(os.environ)
    env["CLAUDE_PROJECT_DIR"] = str(ROOT)
    proc = subprocess.run(
        [sys.executable, str(script)] + list(args),
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        cwd=str(ROOT),
    )
    return proc.returncode, (proc.stderr or "").strip()


def write_payload(file_path, content="contenido de prueba", tool="Write",
                  agent_type=None):
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": tool,
        "tool_input": {"file_path": file_path, "content": content},
    }
    if agent_type:
        payload["agent_type"] = agent_type
    return payload


def bash_payload(command, tool="Bash"):
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": tool,
        "tool_input": {"command": command},
    }


def check(name, expected, got, detail=""):
    ok = expected == got
    _results.append((ok, name, expected, got, detail))
    mark = "OK  " if ok else "FALLA"
    line = "  [%s] %s" % (mark, name)
    if not ok:
        line += "  (esperado %s, obtenido %s) %s" % (expected, got, detail)
    print(line)


def expect_path(name, domain, file_path, expected, agent_type=None,
                tool="Write"):
    code, err = run_hook(
        PATH_GUARD, [domain],
        write_payload(file_path, tool=tool, agent_type=agent_type),
    )
    check(name, expected, code, err[:160])


def expect_bash(name, profile, command, expected, tool="Bash"):
    code, err = run_hook(BASH_GUARD, [profile], bash_payload(command, tool))
    check(name, expected, code, err[:160])


def expect_secret(name, file_path, content, expected):
    code, err = run_hook(
        SECRETS_GUARD, [], write_payload(file_path, content=content)
    )
    check(name, expected, code, err[:160])


# --------------------------------------------------------------------------
# (a) escritura en el dominio propio = permitida
# --------------------------------------------------------------------------
def test_a_dominio_propio():
    print("\n(a) Escritura dentro del dominio propio -> PERMITIDA")
    casos = [
        ("docs", "docs/MVP_SCOPE.md"),
        ("docs", "docs/ADR/ADR-001-hosting.md"),
        ("db", "backend/migrations/versions/0001_inicial.py"),
        ("db", "backend/app/db/models.py"),
        ("db", "docs/DATABASE_SCHEMA.md"),
        ("backend", "backend/app/api/pacientes.py"),
        ("frontend", "frontend/src/pages/Triaje.tsx"),
        ("frontend", "frontend/public/logo.svg"),
        ("qa", "backend/tests/test_pacientes.py"),
        ("qa", "e2e/triaje.spec.ts"),
        ("qa", "tests/integration/test_flujo.py"),
        ("devops", "infra/staging/README.md"),
        ("devops", ".github/workflows/ci.yml"),
        ("devops", "scripts/backup.py"),
        ("devops", "docker-compose.dev.yml"),
        ("devops", "Dockerfile"),
        ("migration", "docs/DATA_MIGRATION_PLAN.md"),
        ("migration", "scripts/migration/cargar_pacientes.py"),
        ("main", "README.md"),
    ]
    for dominio, ruta in casos:
        expect_path("%s -> %s" % (dominio, ruta), dominio, ruta, ALLOW)


# --------------------------------------------------------------------------
# (b) fuera del dominio = bloqueada
# --------------------------------------------------------------------------
def test_b_fuera_de_dominio():
    print("\n(b) Escritura fuera del dominio -> BLOQUEADA")
    casos = [
        ("docs", "backend/app/main.py"),
        ("docs", "frontend/src/App.tsx"),
        ("db", "backend/app/api/pacientes.py"),
        ("db", "docs/MVP_SCOPE.md"),
        ("backend", "backend/migrations/versions/0002_x.py"),
        ("backend", "backend/tests/test_x.py"),
        ("backend", "frontend/src/App.tsx"),
        ("frontend", "backend/app/main.py"),
        ("frontend", "package.json"),
        ("qa", "backend/app/main.py"),
        ("qa", "tests/guards/test_guards.py"),
        ("devops", "scripts/migration/cargar.py"),
        ("devops", "backend/app/main.py"),
        ("migration", "scripts/backup.py"),
        ("migration", "docs/MVP_SCOPE.md"),
    ]
    for dominio, ruta in casos:
        expect_path("%s -> %s" % (dominio, ruta), dominio, ruta, BLOCK)


# --------------------------------------------------------------------------
# (c) ruta con .. o absoluta fuera del repo = bloqueada
# --------------------------------------------------------------------------
def test_c_traversal():
    print("\n(c) Traversal y rutas absolutas fuera del repo -> BLOQUEADAS")
    fuera = str(Path(ROOT).parent / "fuera.txt")
    casos = [
        ("docs", "../fuera.md"),
        ("docs", "docs/../../fuera.md"),
        ("main", "../../otro/archivo.txt"),
        ("main", fuera),
        ("backend", "backend/../../escape.py"),
        ("devops", "..\\..\\escape.yml"),
    ]
    for dominio, ruta in casos:
        expect_path("%s -> %s" % (dominio, ruta), dominio, ruta, BLOCK)

    # Absoluta DENTRO del repo y en dominio: permitida.
    dentro = str(ROOT / "docs" / "NOTA.md")
    expect_path("docs -> absoluta dentro del repo", "docs", dentro, ALLOW)


# --------------------------------------------------------------------------
# (d) docs/APPROVALS.md por CUALQUIER agente o la sesion principal = bloqueada
# --------------------------------------------------------------------------
def test_d_approvals():
    print("\n(d) docs/APPROVALS.md -> BLOQUEADA para todos")
    for dominio in ["docs", "db", "backend", "frontend", "qa", "devops",
                    "migration", "main", "none"]:
        expect_path("%s -> docs/APPROVALS.md" % dominio, dominio,
                    "docs/APPROVALS.md", BLOCK)
    # Tambien por nombre de agente, aunque el argumento diga 'main'.
    for agente in ["medical-architect", "backend-engineer", "final-reviewer",
                   "devops-release-engineer"]:
        expect_path("agente %s -> docs/APPROVALS.md" % agente, "main",
                    "docs/APPROVALS.md", BLOCK, agent_type=agente)
    # Y con separadores de Windows y ruta absoluta.
    expect_path("main -> APPROVALS con separador Windows", "main",
                "docs\\APPROVALS.md", BLOCK)
    expect_path("main -> APPROVALS absoluta", "main",
                str(ROOT / "docs" / "APPROVALS.md"), BLOCK)


# --------------------------------------------------------------------------
# (e) reviewer con git status/diff/log/show = permitido
# --------------------------------------------------------------------------
def test_e_reviewer_permitido():
    print("\n(e) reviewer con git de solo lectura -> PERMITIDO")
    for cmd in ["git status", "git status --short", "git diff",
                "git diff HEAD~1", "git log", "git log --oneline -20",
                "git show HEAD"]:
        expect_bash("reviewer: %s" % cmd, "reviewer", cmd, ALLOW)


# --------------------------------------------------------------------------
# (f) reviewer con rm, >, |, ;, &&, git -c, --output = bloqueado
# --------------------------------------------------------------------------
def test_f_reviewer_bloqueado():
    print("\n(f) reviewer con comandos peligrosos -> BLOQUEADO")
    casos = [
        "rm -rf .",
        "git status > salida.txt",
        "git log | head -5",
        "git status; rm -rf .",
        "git status && rm -rf .",
        "git status || echo malo",
        "git -c core.pager=touch log",
        "git log --output=/tmp/x",
        "git diff --ext-diff",
        "git --git-dir=/otro status",
        "git --work-tree=/otro status",
        "git diff --no-index a b",
        "git log `whoami`",
        "git log $(whoami)",
        "git status\nrm -rf .",
        "python -c \"print(1)\"",
        "pytest",
        "npm run build",
    ]
    for cmd in casos:
        expect_bash("reviewer: %r" % cmd, "reviewer", cmd, BLOCK)


# --------------------------------------------------------------------------
# (g) dev con rm/del/redireccion/powershell = bloqueado
# --------------------------------------------------------------------------
def test_g_dev():
    print("\n(g) dev: allowlist y prohibiciones")
    permitidos = [
        "pytest",
        "pytest backend/tests -q",
        "python -m alembic upgrade head",
        "python tests/guards/test_guards.py",
        "npm run build",
        "npx tsc --noEmit",
        "alembic revision -m inicial",
        "docker compose up -d",
        "git add .",
        "git commit -m mensaje",
        "git switch -c feat/identidad",
        "git status",
    ]
    for cmd in permitidos:
        expect_bash("dev permitido: %r" % cmd, "dev", cmd, ALLOW)

    bloqueados = [
        "rm -rf backend",
        "del /s *.py",
        "pytest > salida.txt",
        "pytest | tee salida.txt",
        "powershell -c Remove-Item x",
        "cmd /c del x",
        "python -m pytest; rm -rf .",
        "sed -i s/a/b/ archivo",
        "mv backend otro",
        "cp -r backend copia",
        "curl http://ejemplo",
        "wget http://ejemplo",
        "ssh servidor",
        "scp archivo servidor:",
        "kubectl get pods",
        "terraform apply",
        "aws s3 ls",
        "git push origin main",
        "git reset --hard HEAD~1",
        "git clean -fd",
        "pytest --deploy staging",
        "alembic upgrade head --prod",
        "echo hola",
        "cat /etc/passwd",
    ]
    for cmd in bloqueados:
        expect_bash("dev bloqueado: %r" % cmd, "dev", cmd, BLOCK)

    # Tambien a traves de la herramienta PowerShell.
    expect_bash("dev bloqueado via PowerShell: Remove-Item", "dev",
                "Remove-Item -Recurse backend", BLOCK, tool="PowerShell")


# --------------------------------------------------------------------------
# (h) escritura en .env = bloqueada
# --------------------------------------------------------------------------
def test_h_env_y_secretos():
    print("\n(h) Rutas de secretos y datos reales -> BLOQUEADAS")
    casos = [
        ("main", ".env"),
        ("main", ".env.local"),
        ("main", "backend/.env"),
        ("backend", "backend/.env.production"),
        ("devops", "infra/claves/servidor.pem"),
        ("devops", "infra/tls/privada.key"),
        ("devops", "secrets/vault.json"),
        ("main", "data/real/pacientes.csv"),
        ("main", "certificados/firma.pfx"),
        ("main", "certificados/firma.p12"),
    ]
    for dominio, ruta in casos:
        expect_path("%s -> %s" % (dominio, ruta), dominio, ruta, BLOCK)

    # .env.example si se permite (es la plantilla sin valores).
    expect_path("main -> .env.example", "main", ".env.example", ALLOW)


# --------------------------------------------------------------------------
# (i) contenido con clave privada o DNI+nombre en fixtures = bloqueado
# --------------------------------------------------------------------------
def test_i_contenido():
    print("\n(i) Contenido con credenciales o datos reales -> BLOQUEADO")
    clave = (
        "-----BEGIN RSA PRIVATE KEY-----\n"
        "MIIEowIBAAKCAQEA0Z3VS5JJcds3xfn/ygWyF\n"
        "-----END RSA PRIVATE KEY-----\n"
    )
    expect_secret("clave privada", "infra/notas.md", clave, BLOCK)
    expect_secret(
        "clave de AWS", "backend/app/config.py",
        "AWS_KEY = 'AKIAIOSFODNN7EXAMPLE1'", BLOCK,
    )
    expect_secret(
        "cadena de conexion con contrasena", "backend/app/db.py",
        "DATABASE_URL = 'postgresql://admin:Sup3rCl4v3@10.0.0.5:5432/med'",
        BLOCK,
    )
    expect_secret(
        "token de GitHub", "scripts/deploy.py",
        "TOKEN = 'ghp_aB3dEfGh1JkLmN0pQrStUvWxYz123456'", BLOCK,
    )
    expect_secret(
        "DNI junto a nombre en fixtures", "backend/tests/fixtures/pacientes.py",
        "PACIENTE = {'nombre': 'Maria Rojas Vasquez', 'dni': '45678912'}",
        BLOCK,
    )
    expect_secret(
        "DNI junto a nombre en e2e", "e2e/datos.ts",
        "const p = { dni: '45678912', nombre: 'Juan Perez Lopez' };", BLOCK,
    )
    # Contenido legitimo: no debe bloquearse.
    expect_secret(
        "placeholder de contrasena", "backend/app/config.py",
        "PASSWORD = os.environ['POSTGRES_PASSWORD']  # nunca literal", ALLOW,
    )
    expect_secret(
        "documentacion sin PHI", "docs/MVP_SCOPE.md",
        "El paciente puede registrarse sin DNI; se usa identificador interno.",
        ALLOW,
    )
    expect_secret(
        "variable de ejemplo", "docs/SETUP_DECISIONS.md",
        "SECRET_KEY=changeme-en-el-vault", ALLOW,
    )


# --------------------------------------------------------------------------
# (j) mayusculas/minusculas y separadores Windows = misma decision
# --------------------------------------------------------------------------
def test_j_normalizacion():
    print("\n(j) Mayusculas/minusculas y separadores -> misma decision")
    pares = [
        # (dominio, canonica, variante, esperado)
        ("docs", "docs/MVP_SCOPE.md", "docs\\MVP_SCOPE.md", ALLOW),
        ("docs", "docs/MVP_SCOPE.md", "DOCS/MVP_SCOPE.md", ALLOW),
        ("docs", "docs/MVP_SCOPE.md", "./docs/MVP_SCOPE.md", ALLOW),
        ("main", "docs/APPROVALS.md", "docs/approvals.md", BLOCK),
        ("main", "docs/APPROVALS.md", "DOCS\\Approvals.MD", BLOCK),
        ("main", ".env", ".ENV", BLOCK),
        ("backend", "frontend/src/App.tsx", "FRONTEND\\src\\App.tsx", BLOCK),
        ("qa", "tests/guards/test_guards.py",
         "TESTS\\GUARDS\\test_guards.py", BLOCK),
    ]
    for dominio, canonica, variante, esperado in pares:
        expect_path("%s canonica %s" % (dominio, canonica), dominio,
                    canonica, esperado)
        expect_path("%s variante  %s" % (dominio, variante), dominio,
                    variante, esperado)


# --------------------------------------------------------------------------
# Extra: dominio `none` bloquea toda escritura; herramientas de edicion
# --------------------------------------------------------------------------
def test_k_extra():
    print("\n(k) Dominio `none`, herramientas de edicion y agentes")
    for ruta in ["docs/nota.md", "backend/app/x.py", "README.md",
                 "frontend/src/App.tsx"]:
        expect_path("none -> %s" % ruta, "none", ruta, BLOCK)

    for tool in ["Edit", "Write", "NotebookEdit", "MultiEdit"]:
        expect_path("none bloquea %s" % tool, "none", "docs/x.md", BLOCK,
                    tool=tool)

    # Herramientas que no escriben: sin decision.
    code, _ = run_hook(PATH_GUARD, ["none"], {
        "tool_name": "Read", "tool_input": {"file_path": "docs/x.md"}})
    check("none no interfiere con Read", ALLOW, code)

    # El agente manda sobre el argumento del hook global.
    expect_path("agente revisor no escribe aunque el hook diga main", "main",
                "backend/app/x.py", BLOCK,
                agent_type="security-privacy-reviewer")
    expect_path("agente docs no escribe backend aunque el hook diga main",
                "main", "backend/app/x.py", BLOCK,
                agent_type="medical-architect")
    expect_path("agente backend si escribe backend", "main",
                "backend/app/x.py", ALLOW, agent_type="backend-engineer")
    expect_path("agente qa no escribe tests/guards", "main",
                "tests/guards/test_guards.py", BLOCK, agent_type="qa-medical")


# --------------------------------------------------------------------------
# Soporte para las pruebas de worktrees y Windows (grupos m..u)
#
# Ejercitan el path_guard.py REAL contra un repositorio sintetico creado en
# un directorio temporal: raiz con .git y worktrees agent-<hex> con su
# archivo .git y el puntero de vuelta. No tocan el .git, el .claude ni
# ningun repositorio real, y no usan mocks.
# --------------------------------------------------------------------------
_skips = []


def skip(name, motivo):
    """Prueba OMITIDA: no cuenta como pasada ni como fallo."""
    _skips.append((name, motivo))
    print("  [SKIP] %s  (%s)" % (name, motivo))


def run_hook_in(project_dir, domain, payload):
    env = dict(os.environ)
    env["CLAUDE_PROJECT_DIR"] = str(project_dir)
    proc = subprocess.run(
        [sys.executable, str(PATH_GUARD), domain],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        cwd=str(project_dir),
    )
    return proc.returncode, (proc.stderr or "").strip()


def expect_in(name, project_dir, domain, file_path, expected,
              agent_type=None, motivo=None):
    """Como expect_path, pero con CLAUDE_PROJECT_DIR propio. Si se espera
    BLOCK y se da `motivo`, el bloqueo debe venir de ese mecanismo (texto
    en stderr) y no de otra regla: asi una prueba no pasa por la razon
    equivocada.
    """
    code, err = run_hook_in(
        project_dir, domain, write_payload(file_path, agent_type=agent_type))
    got = code
    if expected == BLOCK and code == BLOCK and motivo and motivo not in err:
        got = "BLOQUEO por otro motivo: %s" % err[:100]
    check(name, expected, got, err[:160])


class _Repo:
    def __init__(self, base):
        self.tmp = Path(base).resolve()
        self.main = self.tmp / "repo"
        self.outside = self.tmp / "afuera"
        (self.main / ".git" / "worktrees").mkdir(parents=True)
        for sub in ("docs", "backend/app", "frontend/src"):
            (self.main / sub).mkdir(parents=True)
        self.outside.mkdir()
        self._links = []

    def add_worktree(self, hexid, parent=None, dirname=None,
                     admin_parent=None):
        """Crea un worktree como lo hace git: <wt>/.git con `gitdir:` y
        <admin>/gitdir con el puntero de vuelta. Devuelve (wt, admin)."""
        name = "agent-" + hexid
        base = parent or self.main / ".claude" / "worktrees"
        wt = base / (dirname or name)
        admin = (admin_parent or self.main / ".git" / "worktrees") / name
        for d in (wt / "backend" / "app", wt / "frontend" / "src", admin):
            d.mkdir(parents=True)
        (wt / ".git").write_text(
            "gitdir: %s\n" % admin.as_posix(), encoding="utf-8")
        (admin / "gitdir").write_text(
            "%s\n" % (wt / ".git").as_posix(), encoding="utf-8")
        return wt, admin

    def link(self, link, target):
        """Symlink (o junction en Windows). True solo si el enlace existe y
        resuelve de verdad al destino; si no, la prueba debe ser SKIP."""
        try:
            os.symlink(str(target), str(link), target_is_directory=True)
        except (OSError, NotImplementedError):
            if os.name != "nt":
                return False
            res = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(link), str(target)],
                capture_output=True)
            if res.returncode != 0:
                return False
        self._links.append(link)
        try:
            return link.resolve() == Path(target).resolve()
        except OSError:
            return False

    def quitar_enlaces(self):
        for link in self._links:
            try:
                os.rmdir(str(link))
            except OSError:
                try:
                    os.unlink(str(link))
                except OSError:
                    pass


@contextlib.contextmanager
def _repo_sintetico():
    base = tempfile.mkdtemp(prefix="smm_guard_")
    repo = _Repo(base)
    try:
        yield repo
    finally:
        repo.quitar_enlaces()
        shutil.rmtree(base, ignore_errors=True)


# --------------------------------------------------------------------------
# (m) worktree valido: dominio por agente y mismas rutas protegidas
# --------------------------------------------------------------------------
def test_m_worktree_valido():
    print("\n(m) Worktree valido: dominio por agente y rutas protegidas")
    with _repo_sintetico() as r:
        wt, _ = r.add_worktree("a1b2c3")
        casos = [
            # (dominio, agente, ruta relativa al worktree, esperado, motivo)
            ("backend", "backend-engineer", "backend/app/x.py", ALLOW, None),
            ("backend", "backend-engineer", "frontend/src/x.ts", BLOCK,
             "fuera del dominio"),
            ("backend", "backend-engineer", "backend/migrations/versions/x.py",
             BLOCK, "excluido del dominio"),
            ("backend", "backend-engineer", "backend/tests/test_x.py", BLOCK,
             "excluido del dominio"),
            ("frontend", "frontend-medical-ux", "frontend/src/x.ts", ALLOW,
             None),
            ("frontend", "frontend-medical-ux", "frontend/public/x.svg", ALLOW,
             None),
            ("frontend", "frontend-medical-ux", "backend/app/x.py", BLOCK,
             "fuera del dominio"),
            ("frontend", "frontend-medical-ux", "frontend/package.json", ALLOW,
             None),
            ("frontend", "frontend-medical-ux", "package.json", BLOCK,
             "fuera del dominio"),
        ]
        for proyecto, etiqueta in ((wt, "CPD=worktree"), (r.main, "CPD=raiz")):
            for dom, agente, rel, esperado, motivo in casos:
                expect_in("%s [%s] %s" % (agente, etiqueta, rel), proyecto,
                          dom, str(wt / rel), esperado, agent_type=agente,
                          motivo=motivo)
        relativas = [
            ("backend", "backend-engineer", "backend/app/x.py", ALLOW),
            ("backend", "backend-engineer", "frontend/src/x.ts", BLOCK),
            ("frontend", "frontend-medical-ux", "frontend/src/x.ts", ALLOW),
            ("frontend", "frontend-medical-ux", "backend/app/x.py", BLOCK),
        ]
        for dom, agente, rel, esperado in relativas:
            expect_in("%s ruta relativa %s" % (agente, rel), wt, dom, rel,
                      esperado, agent_type=agente, motivo="fuera del dominio")
        # Hook global: el agente manda sobre el argumento del dominio.
        expect_in("hook global: backend-engineer en backend", wt,
                  "main", str(wt / "backend/app/x.py"), ALLOW,
                  agent_type="backend-engineer")
        expect_in("hook global: backend-engineer no escribe frontend",
                  wt, "main", str(wt / "frontend/src/x.ts"), BLOCK,
                  agent_type="backend-engineer", motivo="fuera del dominio")
        # Las mismas rutas protegidas que en la raiz.
        for rel in ("docs/APPROVALS.md", ".claude/settings.json",
                    ".claude/hooks/path_guard.py", ".claude/agents/x.md",
                    "tests/guards/test_guards.py", ".env", "secrets/x.json"):
            expect_in("main protegida en worktree: %s" % rel, wt, "main",
                      str(wt / rel), BLOCK, motivo="ruta protegida")


# --------------------------------------------------------------------------
# (n) worktree invalido, falso, anidado o ausente
# --------------------------------------------------------------------------
def test_n_worktree_invalido():
    print("\n(n) Worktree invalido, falso, anidado o ausente -> BLOQUEADO")
    with _repo_sintetico() as r:
        wt, admin = r.add_worktree("a1b2c3")
        wts = r.main / ".claude" / "worktrees"
        be = "backend/app/x.py"
        falso = wts / "agent-dead01"
        (falso / "backend" / "app").mkdir(parents=True)  # sin archivo .git
        roto = wts / "agent-dead02"
        (roto / "backend" / "app").mkdir(parents=True)
        nada = r.main / ".git" / "worktrees" / "nada"
        (roto / ".git").write_text("gitdir: %s\n" % nada.as_posix(),
                                   encoding="utf-8")
        robado = wts / "agent-dead03"
        (robado / "backend" / "app").mkdir(parents=True)
        (robado / ".git").write_text("gitdir: %s\n" % admin.as_posix(),
                                     encoding="utf-8")
        anidado = wt / ".claude" / "worktrees" / "agent-b1b1b1" / be
        mayus = r.main / ".CLAUDE" / "WORKTREES" / "foo" / be
        fuera = (r.main / "backend" / ".claude" / "worktrees"
                 / "agent-a1b2c3" / be)
        nombre = "no es un nombre de worktree valido"
        sin_git = "no tiene un archivo .git valido"
        casos = [
            ("nombre sin agent-<hex>", wts / "foo" / be, nombre),
            ("nombre agent- con no hex", wts / "agent-xyz" / be, nombre),
            ("nombre agent- sin hex", wts / "agent-" / be, nombre),
            ("mayusculas .CLAUDE/WORKTREES", mayus, nombre),
            ("falso worktree (sin .git)", falso / be, sin_git),
            ("worktree con .git roto", roto / be, sin_git),
            ("worktree con .git ajeno", robado / be, sin_git),
            ("worktree anidado", anidado, "worktree anidado"),
            ("segmento worktrees fuera de raiz", fuera, "fuera de la raiz"),
            ("carpeta .claude/worktrees", wts, "no se escribe sobre"),
            ("carpeta de un worktree", wt, "no se escribe sobre"),
            ("archivo suelto en .claude/worktrees", wts / "x.py",
             "no se escribe sobre"),
        ]
        for nombre_caso, ruta, motivo in casos:
            expect_in("backend-engineer: %s" % nombre_caso, r.main, "backend",
                      str(ruta), BLOCK, agent_type="backend-engineer",
                      motivo=motivo)
        expect_in("anidado con CPD=worktree", wt, "backend", str(anidado),
                  BLOCK, agent_type="backend-engineer",
                  motivo="worktree anidado")
        expect_in("main sin agente tampoco escribe en un worktree falso",
                  r.main, "main", str(falso / be), BLOCK, motivo=sin_git)


# --------------------------------------------------------------------------
# (o) '..' en rutas que involucran worktrees
# --------------------------------------------------------------------------
def test_o_traversal_en_worktree():
    print("\n(o) '..' en rutas que involucran worktrees -> BLOQUEADO")
    with _repo_sintetico() as r:
        wt, _ = r.add_worktree("a1b2c3")
        r.add_worktree("b2c3d4")
        m = r.main
        rel = ".claude/worktrees/agent-a1b2c3"
        casos = [
            # (proyecto, dominio, agente, ruta)
            (wt, "backend", "backend-engineer", "../../../backend/app/x.py"),
            (wt, "backend", "backend-engineer",
             "..\\..\\..\\backend\\app\\x.py"),
            (wt, "backend", "backend-engineer", "backend/../backend/app/x.py"),
            (wt, "frontend", "frontend-medical-ux",
             "frontend/src/../src/x.ts"),
            (wt, "backend", "backend-engineer",
             str(wt / "backend") + "/../frontend/src/x.ts"),
            (wt, "backend", "backend-engineer",
             str(wt / "backend") + "\\..\\..\\..\\..\\..\\fuera.py"),
            (m, "backend", "backend-engineer",
             rel + "/../agent-b2c3d4/backend/app/x.py"),
            (m, "backend", "backend-engineer",
             rel.replace("/", "\\") + "\\..\\agent-b2c3d4\\backend\\app\\x.py"),
            (m, "backend", "backend-engineer",
             "backend/../" + rel + "/backend/app/x.py"),
            (m, "main", None, str(wt) + "/../../../docs/x.md"),
        ]
        for proyecto, dom, agente, ruta in casos:
            expect_in("'..' en worktree: %s" % ruta, proyecto, dom, ruta,
                      BLOCK, agent_type=agente, motivo="usa '..'")
        # Control: sin worktrees de por medio el '..' normal sigue permitido.
        expect_in("control: docs/../docs/x.md fuera de worktrees", m, "docs",
                  "docs/../docs/MVP_SCOPE.md", ALLOW)


# --------------------------------------------------------------------------
# (p) .git protegido: repo principal, worktree y repos anidados
# --------------------------------------------------------------------------
def test_p_git_protegido():
    print("\n(p) .git protegido (repo, worktree, anidados) -> BLOQUEADO")
    with _repo_sintetico() as r:
        wt, _ = r.add_worktree("a1b2c3")
        m = r.main
        casos = [
            # (proyecto, dominio, agente, ruta)
            (m, "main", None, ".git/hooks/x"),
            (m, "main", None, ".git/hooks/pre-commit"),
            (m, "main", None, ".git/config"),
            (m, "main", None, ".git\\config"),
            (m, "main", None, ".git/worktrees/agent-a1b2c3/gitdir"),
            (m, "main", None, "backend/vendor/.git/config"),
            (m, "main", None, "backend/vendor/.git"),
            (m, "main", None, str(m / ".git" / "config")),
            (m, "main", None, str(wt / ".git")),
            (m, "main", None, str(wt / ".git" / "hooks" / "x")),
            (m, "main", None, str(wt / ".git" / "config")),
            (wt, "main", None, ".git"),
            (wt, "main", None, ".git/config"),
            (wt, "main", None, ".git/hooks/x"),
            (wt, "main", None, str(m / ".git" / "config")),
            (wt, "backend", "backend-engineer", str(wt / ".git")),
            (wt, "frontend", "frontend-medical-ux",
             str(wt / "frontend" / "src" / ".git" / "x")),
        ]
        if os.name == "nt":  # el guard ignora mayusculas solo en Windows
            casos.append((m, "main", None, ".GIT/config"))
        for proyecto, dom, agente, ruta in casos:
            expect_in("%s -> %s" % (agente or dom, ruta), proyecto, dom, ruta,
                      BLOCK, agent_type=agente, motivo="ruta protegida")
        # Controles: no se bloquea lo que solo se parece a .git.
        for ruta in (".gitignore", ".github/workflows/ci.yml"):
            expect_in("control: main -> %s" % ruta, m, "main", ruta, ALLOW)


# --------------------------------------------------------------------------
# (q) symlink / junction que escapa del worktree
# --------------------------------------------------------------------------
def _caso_enlace(r, nombre, enlace, destino, proyecto, dominio, agente,
                 ruta, esperado, motivo=None):
    if not r.link(enlace, destino):
        skip(nombre, "no se pudo crear symlink/junction en este entorno")
        return
    expect_in(nombre, proyecto, dominio, str(enlace / ruta), esperado,
              agent_type=agente, motivo=motivo)


def test_q_symlink_junction():
    print("\n(q) Symlink/junction que escapa del worktree -> BLOQUEADO")
    with _repo_sintetico() as r:
        wt_a, _ = r.add_worktree("a1b2c3")
        wt_b, _ = r.add_worktree("b2c3d4")
        m = r.main
        be, fe = "backend-engineer", "frontend-medical-ux"
        _caso_enlace(r, "enlace a carpeta fuera del repo (CPD=worktree)",
                     wt_a / "backend" / "salida", r.outside, wt_a, "backend",
                     be, "x.py", BLOCK, "fuera del repositorio")
        _caso_enlace(r, "enlace a carpeta fuera del repo (CPD=raiz)",
                     wt_a / "backend" / "salida2", r.outside, m, "backend",
                     be, "x.py", BLOCK, "fuera del repositorio")
        _caso_enlace(r, "enlace de frontend a carpeta fuera del repo",
                     wt_a / "frontend" / "src" / "salida", r.outside, wt_a,
                     "frontend", fe, "x.ts", BLOCK, "fuera del repositorio")
        _caso_enlace(r, "enlace de un worktree a otro worktree",
                     wt_a / "backend" / "hacia_b", wt_b / "backend" / "app",
                     wt_a, "backend", be, "x.py", BLOCK, "realpath")
        _caso_enlace(r, "enlace del worktree a docs/ de la raiz",
                     wt_a / "backend" / "hacia_docs", m / "docs", wt_a,
                     "backend", be, "MVP_SCOPE.md", BLOCK, "realpath")
        _caso_enlace(r, "enlace del worktree a docs/ (main sin agente)",
                     wt_a / "backend" / "hacia_docs2", m / "docs", wt_a,
                     "main", None, "APPROVALS.md", BLOCK, "realpath")
        _caso_enlace(r, "enlace de la raiz hacia dentro de un worktree",
                     m / "backend" / "hacia_wt", wt_a / "backend" / "app", m,
                     "backend", be, "x.py", BLOCK, "realpath")
        # Control: un enlace dentro del mismo worktree es legitimo.
        _caso_enlace(r, "control: enlace dentro del mismo worktree permite",
                     wt_a / "backend" / "alias", wt_a / "backend" / "app",
                     wt_a, "backend", be, "x.py", ALLOW)


# --------------------------------------------------------------------------
# (r) Windows: punto/espacio final y Alternate Data Streams
# --------------------------------------------------------------------------
def _mecanismo_windows(r):
    """Demuestra que Windows reinterpreta estas formas (por eso se bloquean)."""
    nombre = "mecanismo Windows: punto final y ADS"
    if os.name != "nt":
        skip(nombre, "no es Windows")
        return
    base = r.tmp / "mecanismo.txt"
    base.write_text("base", encoding="utf-8")
    try:
        with open(str(base) + ".", "a", encoding="utf-8") as f:
            f.write("+punto")
        with open(str(base) + "::$DATA", "a", encoding="utf-8") as f:
            f.write("+ads")
        contenido = base.read_text(encoding="utf-8")
    except OSError as e:
        skip(nombre, "no se pudo abrir: %s" % e)
        return
    check("Windows: 'archivo.' escribe sobre 'archivo'", True,
          "+punto" in contenido)
    check("Windows: 'archivo::$DATA' escribe sobre 'archivo'", True,
          "+ads" in contenido)


def test_r_windows_punto_espacio_ads():
    print("\n(r) Windows: punto/espacio final y ADS -> BLOQUEADOS")
    with _repo_sintetico() as r:
        wt, _ = r.add_worktree("a1b2c3")
        m = r.main
        sp = "\x20"
        aprob = str(m / "docs" / "APPROVALS.md")
        be = "backend-engineer"
        esp = "espacio"
        ads = "contiene ':'"
        casos = [
            # (proyecto, dominio, agente, ruta, motivo)
            (m, "main", None, "docs/APPROVALS.md.", esp),
            (m, "main", None, "docs/APPROVALS.md" + sp, esp),
            (m, "main", None, "docs/APPROVALS.md..", esp),
            (m, "main", None, sp + "docs/APPROVALS.md", esp),
            (m, "main", None, "docs./APPROVALS.md", esp),
            (m, "main", None, "docs" + sp + "/APPROVALS.md", esp),
            (m, "main", None, "docs/approvals.md.", esp),
            (m, "main", None, aprob + ".", esp),
            (m, "main", None, ".env.", esp),
            (m, "main", None, ".env" + sp, esp),
            (m, "main", None, "secrets/vault.json.", esp),
            (m, "qa", None, "tests/guards/test_guards.py.", esp),
            (m, "backend", be, "backend/app/x.py.", esp),
            (wt, "backend", be,
             str(wt / "backend" / "app" / "x.py") + sp, esp),
            (m, "main", None, "docs/APPROVALS.md::$DATA", ads),
            (m, "main", None, "docs/APPROVALS.md:flujo", ads),
            (m, "main", None, "docs/APPROVALS.md:flujo:$DATA", ads),
            (m, "main", None, "docs/APPROVALS.md::$data", ads),
            (m, "main", None, "docs/approvals.md::$DATA", ads),
            (m, "main", None, ".env::$DATA", ads),
            (m, "docs", None, "docs/x.md:Zone.Identifier", ads),
            (m, "main", None, aprob + "::$DATA", ads),
            (m, "backend", be, "backend/app/x.py::$DATA", ads),
            (wt, "backend", be,
             str(wt / "backend" / "app" / "x.py") + "::$DATA", ads),
            (m, "main", None, "C:docs/x.md", ads),
        ]
        for proyecto, dom, agente, ruta, motivo in casos:
            expect_in("%s -> %r" % (agente or dom, ruta), proyecto, dom,
                      ruta, BLOCK, agent_type=agente, motivo=motivo)
        _mecanismo_windows(r)


# --------------------------------------------------------------------------
# (s) nombres cortos 8.3: solo con un alias verificable en este volumen
# --------------------------------------------------------------------------
def _nombre_corto(path):
    """Nombre corto 8.3 que el SO asigna a `path`; None si no hay uno real."""
    if os.name != "nt":
        return None
    try:
        import ctypes
        buf = ctypes.create_unicode_buffer(32768)
        n = ctypes.windll.kernel32.GetShortPathNameW(str(path), buf, len(buf))
    except (ImportError, OSError, AttributeError):
        return None
    return buf.value if n else None


def test_s_nombre_corto_83():
    print("\n(s) Nombres cortos 8.3 -> BLOQUEADOS")
    with _repo_sintetico() as r:
        largo = r.main / "docs" / "aprobaciones_largas_de_prueba.md"
        largo.write_text("alias", encoding="utf-8")
        corto = _nombre_corto(largo)
        real = False
        if corto and "~" in Path(corto).name:
            try:
                real = Path(corto).read_text(encoding="utf-8") == "alias"
            except OSError:
                real = False
        if real:
            check("el nombre corto %s es un alias real del archivo largo"
                  % Path(corto).name, True, real)
            expect_in("8.3 relativo: docs/%s" % Path(corto).name, r.main,
                      "main", "docs/" + Path(corto).name, BLOCK, motivo="8.3")
            expect_in("8.3 absoluto: %s" % Path(corto).name, r.main, "main",
                      corto, BLOCK, motivo="8.3")
        else:
            skip("alias 8.3 real",
                 "este SO/volumen no genera nombres cortos 8.3 verificables")
        # Politica explicita (no se afirma equivalencia con ningun archivo).
        expect_in("politica: todo componente con ~N se bloquea", r.main,
                  "docs", "docs/ARCHIV~1.MD", BLOCK, motivo="8.3")
        expect_in("control: '~' sin digito no se bloquea", r.main, "docs",
                  "docs/version~final.md", ALLOW)


# --------------------------------------------------------------------------
# (t) dispositivos Windows y rutas UNC / extendidas
# --------------------------------------------------------------------------
def test_t_dispositivos_y_rutas_extendidas():
    print("\n(t) Dispositivos Windows y rutas UNC/extendidas -> BLOQUEADOS")
    with _repo_sintetico() as r:
        wt, _ = r.add_worktree("a1b2c3")
        m = r.main
        be = "backend-engineer"
        disp = "nombre de dispositivo"
        for nombre in ("NUL", "nul", "NUL.md", "CON", "con.txt", "PRN", "AUX",
                       "aux.md", "COM1", "LPT1.txt", "CONIN$", "CONOUT$"):
            expect_in("docs -> docs/%s" % nombre, m, "docs",
                      "docs/" + nombre, BLOCK, motivo=disp)
        expect_in("main -> NUL en la raiz", m, "main", "NUL", BLOCK,
                  motivo=disp)
        expect_in("backend -> backend/app/aux.py", m, "backend",
                  "backend/app/aux.py", BLOCK, agent_type=be, motivo=disp)
        expect_in("backend en worktree -> .../NUL", wt, "backend",
                  str(wt / "backend" / "app" / "NUL"), BLOCK, agent_type=be,
                  motivo=disp)
        for nombre in ("consola.md", "auxiliar.md", "nulo.md", "connect.md"):
            expect_in("control: docs/%s no es dispositivo" % nombre, m, "docs",
                      "docs/" + nombre, ALLOW)
        # Rutas UNC, de dispositivo y extendidas (\\?\, \\.\).
        unc = "prefijo UNC"
        casos = [
            (m, "main", None, "\\\\?\\" + str(m / "docs" / "x.md")),
            (m, "main", None, "\\\\?\\" + str(m / "docs" / "APPROVALS.md")),
            (m, "main", None, "\\\\.\\" + str(m / "docs" / "x.md")),
            (m, "main", None, "\\\\?\\UNC\\servidor\\recurso\\x.md"),
            (m, "main", None, "\\\\servidor\\recurso\\docs\\x.md"),
            (m, "main", None, "//?/" + str(m / "docs" / "x.md")),
            (wt, "backend", be,
             "\\\\?\\" + str(wt / "backend" / "app" / "x.py")),
        ]
        for proyecto, dom, agente, ruta in casos:
            expect_in("extendida/UNC: %s" % ruta, proyecto, dom, ruta, BLOCK,
                      agent_type=agente, motivo=unc)


# --------------------------------------------------------------------------
# (u) fail-closed: CLAUDE_PROJECT_DIR invalido, inconsistente o no verificable
# --------------------------------------------------------------------------
def _fail_closed(nombre, proyecto):
    expect_in("fail-closed: %s" % nombre, proyecto, "backend",
              "backend/app/x.py", BLOCK, agent_type="backend-engineer",
              motivo="no se pudo determinar con certeza")


def test_u_fail_closed():
    print("\n(u) CLAUDE_PROJECT_DIR invalido o no verificable -> BLOQUEADO")
    with _repo_sintetico() as r:
        wts = r.main / ".claude" / "worktrees"
        wt, _ = r.add_worktree("a1b2c3")
        # Control: el mismo destino con un worktree valido SI se permite.
        expect_in("control: CPD=worktree valido permite", wt, "backend",
                  "backend/app/x.py", ALLOW, agent_type="backend-engineer")

        roto = wts / "agent-c0ffee"
        roto.mkdir(parents=True)
        nada = (r.main / ".git" / "worktrees" / "nada").as_posix()
        (roto / ".git").write_text("gitdir: %s\n" % nada, encoding="utf-8")
        _fail_closed(".git apunta a un gitdir inexistente", roto)

        sin_git = wts / "agent-c0ffe1"
        sin_git.mkdir()
        _fail_closed("carpeta de worktree sin archivo .git", sin_git)

        dos, _ = r.add_worktree("d1d1d1")
        with open(str(dos / ".git"), "a", encoding="utf-8") as f:
            f.write("segunda linea\n")
        _fail_closed(".git con mas de una linea", dos)

        sin_prefijo, _ = r.add_worktree("d2d2d2")
        (sin_prefijo / ".git").write_text("ref: refs/heads/x\n",
                                          encoding="utf-8")
        _fail_closed(".git sin prefijo gitdir:", sin_prefijo)

        ajeno, adm = r.add_worktree("e1e1e1")
        (adm / "gitdir").write_text(
            "%s\n" % (wt / ".git").as_posix(), encoding="utf-8")
        _fail_closed("puntero de vuelta apunta a otro worktree", ajeno)

        sin_vuelta, adm = r.add_worktree("e2e2e2")
        (adm / "gitdir").unlink()
        _fail_closed("sin puntero de vuelta (admin/gitdir)", sin_vuelta)

        lugar, _ = r.add_worktree("f1f1f1", parent=r.main / "otro")
        _fail_closed("worktree fuera de .claude/worktrees", lugar)

        admin_falso, _ = r.add_worktree(
            "a7a7a7", admin_parent=r.main / "falso" / "worktrees")
        _fail_closed("gitdir fuera de <raiz>/.git/worktrees", admin_falso)

        nombre_mal, _ = r.add_worktree("b9b9b9", dirname="zzz")
        _fail_closed("worktree sin nombre agent-<hex>", nombre_mal)

        _fail_closed("subcarpeta de un worktree valido", wt / "backend")

        principal = r.tmp / "repo2"
        principal.mkdir()
        (principal / ".git").write_text("gitdir: x\n", encoding="utf-8")
        _fail_closed("raiz con .git como archivo no verificable", principal)


# --------------------------------------------------------------------------
# (v) frontend-medical-ux: configuracion de frontend/ por allowlist exacta
# --------------------------------------------------------------------------
def test_v_frontend_config():
    print("\n(v) frontend-medical-ux: configs de frontend/ por allowlist exacta")
    agente = "frontend-medical-ux"
    permitidas = [
        "frontend/src/main.tsx",
        "frontend/public/favicon.svg",
        "frontend/package.json",
        "frontend/package-lock.json",
        "frontend/vite.config.ts",
        "frontend/vite.config.js",
        "frontend/tsconfig.json",
        "frontend/tsconfig.app.json",
        "frontend/index.html",
        "frontend/eslint.config.js",
    ]
    fuera_de_dominio = [
        "package.json",
        "vite.config.ts",
        "tsconfig.json",
        "backend/package.json",
        "infra/package.json",
        "docs/package.json",
        ".claude/package.json",
        # Fuera del alcance de P1: siguen bloqueadas hasta demostrar que se necesitan.
        "frontend/tailwind.config.js",
        "frontend/postcss.config.js",
        "frontend/Dockerfile",
        "frontend/sub/package.json",
        "frontend/package.json.bak",
        "frontend/tests/x.spec.ts",
        "frontend/node_modules/x/package.json",
    ]
    protegidas = [
        "tests/guards/package.json",
        ".claude/hooks/package.json",
        "frontend/.env",
    ]
    # Mismo resultado con el dominio del argumento y con el hook global
    # (el agente manda sobre el argumento).
    for dom in ("frontend", "main"):
        for ruta in permitidas:
            expect_in("%s [arg=%s] permite %s" % (agente, dom, ruta), ROOT,
                      dom, ruta, ALLOW, agent_type=agente)
        for ruta in fuera_de_dominio:
            expect_in("%s [arg=%s] bloquea %s" % (agente, dom, ruta), ROOT,
                      dom, ruta, BLOCK, agent_type=agente,
                      motivo="fuera del dominio")
        for ruta in protegidas:
            expect_in("%s [arg=%s] bloquea %s" % (agente, dom, ruta), ROOT,
                      dom, ruta, BLOCK, agent_type=agente,
                      motivo="ruta protegida")
    # Ningun otro agente gana acceso a frontend/package.json.
    otros = [
        ("docs", "medical-architect"),
        ("db", "database-architect"),
        ("backend", "backend-engineer"),
        ("qa", "qa-medical"),
        ("devops", "devops-release-engineer"),
    ]
    for dom, otro in otros:
        expect_in("%s no escribe frontend/package.json" % otro, ROOT, dom,
                  "frontend/package.json", BLOCK, agent_type=otro,
                  motivo="fuera del dominio")


def main():
    print("Pruebas de guardrails - SISTEMAMEDIC")
    print("Raiz del proyecto: %s" % ROOT)
    for faltante in [p for p in (PATH_GUARD, BASH_GUARD, SECRETS_GUARD)
                     if not p.exists()]:
        print("ERROR: falta el hook %s" % faltante)
        return 1

    test_a_dominio_propio()
    test_b_fuera_de_dominio()
    test_c_traversal()
    test_d_approvals()
    test_e_reviewer_permitido()
    test_f_reviewer_bloqueado()
    test_g_dev()
    test_h_env_y_secretos()
    test_i_contenido()
    test_j_normalizacion()
    test_k_extra()
    test_m_worktree_valido()
    test_n_worktree_invalido()
    test_o_traversal_en_worktree()
    test_p_git_protegido()
    test_q_symlink_junction()
    test_r_windows_punto_espacio_ads()
    test_s_nombre_corto_83()
    test_t_dispositivos_y_rutas_extendidas()
    test_u_fail_closed()
    test_v_frontend_config()

    total = len(_results)
    fallos = [r for r in _results if not r[0]]
    print("\n" + "=" * 70)
    print("RESULTADO: %d/%d pasadas" % (total - len(fallos), total))
    if _skips:
        print("OMITIDAS: %d (no cuentan como pasadas)" % len(_skips))
        for nombre, motivo in _skips:
            print("  - %s: %s" % (nombre, motivo))
    if fallos:
        print("\nFALLAS:")
        for _, name, exp, got, detail in fallos:
            print("  - %s: esperado %s, obtenido %s. %s"
                  % (name, exp, got, detail))
        print("\nCorrige el GUARD, nunca el test.")
        return 1
    print("Todos los guardrails se comportan como deben.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
