# CLAUDE.md - SISTEMAMEDIC

## 1. Propósito, usuarios y entorno

Sistema integral de atención y gestión clínica para la IPRESS del Centro Médico, Parroquia
San Martín de Porres, **Iquitos**. Usuarios: recepción/admisión, enfermería y triaje, médicos,
laboratorio, farmacia, caja/administración, dirección médica, profesionales visitantes de campañas.

Condiciones reales que el diseño debe asumir:

- **Cortes de energía** y **conectividad irregular**: modo degradado y recuperación son requisitos, no extras.
- **Campañas internacionales** con profesionales visitantes temporales.
- **Pacientes sin DNI**, menores, extranjeros, personas de comunidades ribereñas y **emergencias** sin filiación previa.
- PC compartidas en recepción y consultorios.

## 2. Reglas innegociables

- **Una identidad de paciente y una HCE longitudinal.** La atención de campaña usa la misma HCE
  (un `Encounter` con `campaign_id` opcional); jamás una base paralela.
- **DNI no es obligatorio.** `patient_identifiers` admite múltiples documentos (DNI, CE, pasaporte, CPP u otros)
  y **siempre** existe un identificador interno. Hay flujo NN/emergencia y **merge auditado**.
- **Autorización siempre en el backend.** Ocultar un botón en el frontend no es seguridad.
- **Lo clínico cerrado o firmado no se sobrescribe ni se elimina.** Las correcciones son por
  addendum/versionado, con autor, fecha y motivo.
- **Auditoría de accesos y cambios sensibles con integridad verificable** (append-only o hash encadenado;
  se decide en ADR-006). **Sin PHI en logs**: solo IDs técnicos y correlación.
- **Mínimo privilegio.** Separar filiación, clínica, caja y administración.
- **Solo datos sintéticos en DEV y en cualquier IA** (`docs/TEST_DATA_POLICY.md`). Claude Code **no tiene
  credenciales ni acceso a staging/PROD**. El despliegue va solo por CI/CD con aprobación humana. Las
  migraciones con datos reales las ejecuta una persona autorizada en entorno aislado, sin Claude Code.
- **MFA obligatorio desde F5** para administradores y médicos: TOTP o FIDO2/passkey. **SMS no es método
  principal.** Cuentas personales, nunca compartidas. En PC compartida: bloqueo rápido y reautenticación
  para acciones sensibles.
- **Break-glass** solo con motivo obligatorio, tiempo limitado, alerta inmediata y revisión posterior.
- **Cuentas de profesionales visitantes**: temporales, con fecha de vencimiento, MFA y mínimo privilegio.
- **Tiempo**: se guarda en **UTC**, se muestra en **America/Lima**.
- **La IA no diagnostica, no prescribe, no da altas ni decide clínicamente.**

## 3. Cumplimiento

Marco aplicable (detalle y fuentes en `docs/regulatory/NORMATIVE_MATRIX.md`):

- Ley 29733 (protección de datos personales) y **DS 016-2024-JUS** (reglamento).
- **NTS 139** - MINSA (RM 214-2018/MINSA): historia clínica.
- **RM 462-2023/MINSA**: firma digital en documentos clínicos.
- **SIHCE**: RM 164-2025, RM 188-2026, RM 673-2025.
- **SUNAT / CPE** según el RUC y régimen del Centro Médico.

Reglas de uso de la normativa:

1. Toda afirmación normativa requiere **fuente oficial, verificador (nombre y rol) y fecha**.
   Sin eso se escribe **"POR VERIFICAR"**. No se cita de memoria.
2. El término correcto en el marco peruano es **EIPD** (evaluación de impacto en la protección de datos),
   no "DPIA".
3. El plazo de notificación de incidentes de 48 h (DS 016-2024-JUS art. 34) está **POR VALIDAR con asesor**.

## 4. Stack

- **Backend**: FastAPI + SQLAlchemy + Alembic + Pydantic.
- **Frontend**: React + TypeScript + Vite + Tailwind.
- **Datos**: PostgreSQL.
- **Entorno**: Docker Compose (dev).
- **Pruebas**: pytest + Playwright.
- **CI**: lint, typecheck, tests, build, escaneo de dependencias y escaneo de secretos.

## 5. Mapa de agentes

El agente principal **coordina**; no hace todo. Cada subagente escribe solo en su dominio
(forzado por `.claude/hooks/path_guard.py`, no por buena voluntad).

| Agente | Rol | Escribe en |
|---|---|---|
| `medical-architect` | Diseño clínico-funcional y ADR | `docs/**` (nunca `docs/APPROVALS.md`) |
| `clinical-workflow-reviewer` | Revisa máquinas de estado clínicas | nada |
| `database-architect` | Modelo y migraciones | `backend/migrations/**`, `backend/app/db/**`, `docs/DATABASE_SCHEMA.md` |
| `backend-engineer` | API y lógica | `backend/**` salvo migraciones y tests |
| `frontend-medical-ux` | Interfaz clínica | `frontend/src/**`, `frontend/public/**` |
| `security-privacy-reviewer` | Seguridad y privacidad | nada (reporta) |
| `qa-medical` | Pruebas | `backend/tests/**`, `frontend/tests/**`, `e2e/**`, `tests/**` salvo `tests/guards/**` |
| `devops-release-engineer` | Infra, CI, scripts | `infra/**`, `.github/**`, `scripts/**` salvo `scripts/migration/**`, compose/Dockerfile |
| `data-migration-reviewer` | Plan de migración | `docs/DATA_MIGRATION_PLAN.md`, `scripts/migration/**` |
| `final-reviewer` | Veredicto P0/P1/P2 | nada |

## 6. Ciclo por feature

`medical-architect` → `clinical-workflow-reviewer` → `database-architect` →
`backend-engineer` + `frontend-medical-ux` (en worktrees si van en paralelo; **nunca dos escritores
sobre los mismos archivos**) → `qa-medical` → `security-privacy-reviewer` → `final-reviewer` →
corregir y repetir **hasta cero P0 y cero P1** → documentar.

Los revisores independientes corren en paralelo. Ramas `feat/<tema>`, commits pequeños,
nada de trabajo directo en `main`.

## 7. Definition of Done (11 dimensiones)

Una feature está terminada solo si cumple las once:

1. **Funcional**: cumple el criterio de aceptación escrito.
2. **Clínica**: estados y flujos validados contra `clinical-workflows`.
3. **Privacidad**: minimización por rol, base jurídica, sin PHI en logs.
4. **Seguridad**: autorización en backend, pruebas negativas e IDOR.
5. **Datos**: migración no destructiva, índices, integridad referencial.
6. **Pruebas**: unitarias, integración, E2E y casos negativos.
7. **Observabilidad**: logs útiles sin PHI, health check, métrica relevante.
8. **Continuidad**: comportamiento ante caída, reintento y modo degradado.
9. **Documentación**: actualizada en `docs/` y en el runbook si aplica.
10. **Capacitación**: material o nota para el área usuaria.
11. **Entrega**: CI verde, commit en rama, `docs/PROGRESS.md` actualizado.

**Todo bug corregido añade un test de regresión.**

## 8. Revisión humana obligatoria

Requieren **revisión humana técnica independiente** antes de avanzar de fase:
autenticación, RBAC, break-glass, auditoría e inmutabilidad de la HCE.

## 9. Modo de trabajo

- **Plan mode** solo para diseñar features. Implementación en **accept edits** con `allow`/`deny` y hooks.
- **Nunca `bypassPermissions`.** Nunca push forzado. Nunca push a `main`.
- Si un hook te bloquea: **repórtalo y sigue con otra tarea.** No lo edites ni lo evadas.
- Ninguna salida de una IA es una aprobación. `docs/APPROVALS.md` lo escribe solo una persona.

## 10. Dependencia de una persona

Riesgo identificado: el proyecto no puede depender de un único responsable técnico.
Mitigación obligatoria: **runbooks escritos**, repositorio y cuentas **institucionales**, y
**mínimo dos maintainers** por recurso (`docs/CUSTODY_REGISTER.md`).

## 11. Aviso

Nada de lo producido aquí sustituye validación clínica, legal, tributaria ni de protección de datos
por profesionales responsables.
