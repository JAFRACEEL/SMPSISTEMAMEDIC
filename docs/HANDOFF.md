# Handoff - SISTEMAMEDIC

**Fecha: 2026-10-02.** Para quien retome, sea una persona o una nueva sesión de Claude Code.
Léelo junto con `docs/PROGRESS.md` y `docs/APPROVALS.md`.

## Estado actual

- **Rama:** `feat/base-tecnica`. **HEAD:** `41da8df`. `git status` limpio.
- **H1: CERRADO Y APROBADO HUMANAMENTE.** 319/319 guardrails PASS, `git diff --check` limpio.
  A5 queda como riesgo residual aceptado y documentado. No reabrir H1 salvo regresión real.
- **F2 Discovery: EN CURSO.** **H2 NO está aprobado.** Bloque 1b pendiente de respuestas de Franco.
  Bloque 2 registrado como NO DEFINIDO / pendiente. No inventar datos de la IPRESS.

## Base técnica: INTEGRADA, NO VALIDADA

Integración manual en `feat/base-tecnica`:

| Parte | Commit de agente | Merge |
|---|---|---|
| Backend | `2ddc472` | `e099fd4` |
| Frontend (parcial) | `c9a55ee` | `39923f5` |
| Infra / CI | `4b1e98a` | `41da8df` |

Los tres worktrees de implementación se eliminaron tras comprobar que estaban limpios; no hay
worktrees activos aparte del principal. (Las ramas locales `worktree-agent-*` aún existen como ramas.)
Nota de cierre: `git worktree list --porcelain` lo bloqueó `bash_guard` en esta sesión; la ausencia de
worktrees se toma del cierre manual previo, no de una verificación nueva.

Contenido integrado:

- **Backend:** `backend/README.md`, `backend/app/`, `backend/pyproject.toml`.
- **Frontend (parcial):** `frontend/public/`, `frontend/src/`. Faltan configs raíz de `frontend/`:
  `package.json`, `package-lock.json`, `vite.config.*`, `tsconfig*.json`, `index.html`, `eslint.config.*`.
- **Infra/CI:** `.github/workflows/ci.yml`, `docker-compose.yml`, `infra/docker/`, `infra/env/dev.env.example`.

**Aún no se ha ejecutado como conjunto:** backend, frontend, Docker Compose, CI, pruebas integradas,
revisión Codex y revisión final.

## Pendientes técnicos

- **P1 Ownership frontend:** `frontend-medical-ux` necesita acceso controlado a ciertos archivos de
  `frontend/`. No ampliar permisos a `package.json` de la raíz del repo. Cambio mínimo en `path_guard`,
  con tests de regresión, aplicado por una persona.
- **P2 Health endpoint:** inconsistencia frontend `/api/health` vs backend `/health`. Unificar antes de validar.
- **P3 `.env.example`:** no relajar la protección global de `.env*`. Existe `infra/env/dev.env.example`.
  Si se crea `/.env.example`, excepción exacta solo para ese archivo.
- **P4 Line endings:** avisos "LF will be replaced by CRLF". Evaluar `.gitattributes` con `eol=lf`
  (sobre todo Docker/CI).
- **P5 Backup/restore:** falta script/procedimiento.
- **P6 GitHub:** falta protección de rama.
- **P7 Validación integrada:** ver lista arriba.

## Orden de la próxima sesión

1. Leer este archivo. 2. Verificar `git status` y rama. 3. Resolver ownership frontend.
4. Completar scaffold frontend. 5. Resolver `.env.example`. 6. Unificar health endpoint.
7. Crear/validar `.gitattributes`. 8. Backup/restore mínimo. 9. Ejecutar backend. 10. Ejecutar frontend.
11. Ejecutar Docker Compose. 12. Tests/CI local si es posible. 13. Revisión Codex/diff.
14. Corregir hallazgos. 15. Continuar Discovery F2 en paralelo. 16. No aprobar H2 hasta validar Discovery real.

## NO HACER

- No reconstruir H1, no recrear worktrees antiguos, no reaplicar patches de H1.
- No ampliar `bash_guard` por comodidad.
- No usar `git clean` indiscriminadamente.
- No programar módulos clínicos todavía.
- No inventar datos institucionales.
- No marcar H2 aprobado.
- No usar datos reales de pacientes.

**BASE TÉCNICA INTEGRADA, NO VALIDADA. H1 APROBADO. H2 NO APROBADO.**
