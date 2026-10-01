# Registro de aprobaciones - SISTEMAMEDIC

> **Este archivo SOLO lo edita una persona. Los agentes de IA no pueden escribirlo.**
>
> Está denegado por `permissions.deny` en `.claude/settings.json` y bloqueado por el hook
> `path_guard.py` para TODOS los dominios, incluida la sesión principal.
>
> Reglas:
> - Un gate queda habilitado únicamente cuando su fila dice `APROBADO` **y** tiene aprobador (nombre y rol) y fecha.
> - Ninguna salida de una IA cuenta como aprobación.
> - Formato de fecha obligatorio: `AAAA-MM-DD`.
> - "Evidencia" = enlace, acta, ruta de archivo o identificador de commit que sustenta la aprobación.

## Gates principales (Oleada A)

| Gate | Alcance | Estado | Aprobador (nombre y rol) | Fecha | Evidencia |
|---|---|---|---|---|---|
| H1 | F0 + F1 técnica: entorno Claude Code, agentes, skills, guardrails, borradores F0 | APROBADO | Franco López — Responsable del proyecto | 2026-10-01 | `tests/guards/test_guards.py`: 319/319 PASS; `git diff --check`: sin errores; validación live de dominios backend/frontend en worktrees; A5 aceptado como riesgo residual |
| H2 | Discovery F2 completado y validado | PENDIENTE | | | |
| H3 | ADR de arquitectura aprobados (F3) | PENDIENTE | | | |
| H4 | F4 + F4b: scaffold, CI, backup/restore probado, staging aprovisionado | PENDIENTE | | | |
| H5 | F5: auth, MFA, RBAC, break-glass, auditoría de acceso (revisión técnica independiente) | PENDIENTE | | | |
| H6 | F6: identidad, consentimientos, agenda, check-in, triaje (UAT recepción y triaje) | PENDIENTE | | | |
| H7 | F7: HCE, firma/cierre, addendum, recetas, CIE-10, auditoría íntegra | PENDIENTE | | | |
| H8 | F8A: E2E, performance, simulacro de caída/restore, release candidate | PENDIENTE | | | |
| H9 | F9A: hardening y pentest externo con remediación | PENDIENTE | | | |
| H10 | F10A: plan y ensayo de migración de datos | PENDIENTE | | | |
| H11 | F11A: PROD aprovisionado y operación en paralelo | PENDIENTE | | | |
| H12 | F12A: go-live de la Oleada A e hypercare | PENDIENTE | | | |

## Gates por oleada (B, C, D, E)

| Oleada | Hito | Estado | Aprobador (nombre y rol) | Fecha | Evidencia |
|---|---|---|---|---|---|
| B | UAT del área | PENDIENTE | | | |
| B | Retest de seguridad focal | PENDIENTE | | | |
| B | Migración/configuración de datos | PENDIENTE | | | |
| B | Operación en paralelo | PENDIENTE | | | |
| B | Go-live | PENDIENTE | | | |
| C | UAT del área | PENDIENTE | | | |
| C | Retest de seguridad focal | PENDIENTE | | | |
| C | Migración/configuración de datos | PENDIENTE | | | |
| C | Operación en paralelo | PENDIENTE | | | |
| C | Go-live | PENDIENTE | | | |
| D | UAT del área | PENDIENTE | | | |
| D | Retest de seguridad focal | PENDIENTE | | | |
| D | Migración/configuración de datos | PENDIENTE | | | |
| D | Operación en paralelo | PENDIENTE | | | |
| D | Go-live | PENDIENTE | | | |
| E | UAT del área | PENDIENTE | | | |
| E | Retest de seguridad focal | PENDIENTE | | | |
| E | Migración/configuración de datos | PENDIENTE | | | |
| E | Operación en paralelo | PENDIENTE | | | |
| E | Go-live | PENDIENTE | | | |

## Aprobación de ADR

Los ADR se aprueban en `docs/ADR/`. Esta tabla replica su estado para el control de gates.

| ADR | Tema | Estado | Aprobador (nombre y rol) | Fecha |
|---|---|---|---|---|
| ADR-001 | Hosting, RPO/RTO y modo degradado | PROPUESTO | | |
| ADR-002 | Identidad del paciente (identificadores múltiples, NN, merge) | PROPUESTO | | |
| ADR-003 | HCE: firma, addendum, versionado y retención | PROPUESTO | | |
| ADR-004 | Privacidad y EIPD | PROPUESTO | | |
| ADR-005 | Break-glass | PROPUESTO | | |
| ADR-006 | Auditoría con integridad verificable | PROPUESTO | | |
| ADR-007 | Idioma/i18n y zona horaria | PROPUESTO | | |
| ADR-008 | Almacenamiento de adjuntos | PROPUESTO | | |
| ADR-009 | Entornos staging y PROD (aprovisionamiento, TLS, dominio, vault) | PROPUESTO | | |

### Evidencia H1 — 2026-10-01

**Aprobado por:** Franco López — Responsable del proyecto

- 319/319 pruebas de guardrails aprobadas.
- `git diff --check` sin errores.
- `backend-engineer`: permite backend y bloquea frontend en worktree.
- `frontend-medical-ux`: permite frontend y bloquea backend en worktree.
- Pruebas de regresión añadidas para worktrees, `.git`, traversal, Windows, ADS, symlink/junction y fail-closed.
- A5 permanece como riesgo residual documentado y aceptado.
