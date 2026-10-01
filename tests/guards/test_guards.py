#!/usr/bin/env python3
"""Pruebas de violacion de los guardrails de SISTEMAMEDIC.

Solo biblioteca estandar. Alimentan los hooks de .claude/hooks/ con JSON
simulado por stdin y verifican el codigo de salida.

    0 = permitido (sin decision)
    2 = bloqueado

Uso:  python tests/guards/test_guards.py
Debe pasar al 100 %. Si una prueba falla, SE CORRIGE EL GUARD, NUNCA EL TEST.
"""

import json
import os
import subprocess
import sys
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
        ("frontend", "frontend/package.json"),
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

    total = len(_results)
    fallos = [r for r in _results if not r[0]]
    print("\n" + "=" * 70)
    print("RESULTADO: %d/%d pasadas" % (total - len(fallos), total))
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
