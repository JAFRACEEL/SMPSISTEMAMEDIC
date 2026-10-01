# Avance - SISTEMAMEDIC

Quien retome el trabajo: **lee este archivo y `docs/APPROVALS.md`, y sigue en el primer ítem
sin marcar.** Última actualización: **2026-10-01**.

## Estado general

| Fase | Estado | Gate | Estado del gate |
|---|---|---|---|
| **SETUP (F0 + F1 técnica)** | **COMPLETADA** | H1 | **PENDIENTE DE APROBACIÓN HUMANA** |
| S-DISCOVERY (consolidación F2) | No iniciada | H2 / H3 | Pendiente |
| F4 + F4b (scaffold, CI, staging) | No iniciada | H4 | Pendiente |
| F5 (auth, MFA, RBAC, break-glass) | No iniciada | H5 | Pendiente |
| F6 (identidad, agenda, triaje) | No iniciada | H6 | Pendiente |
| F7 (HCE, firma, recetas) | No iniciada | H7 | Pendiente |
| F8A (E2E, performance, RC) | No iniciada | H8 | Pendiente |
| F9A-PREP (hardening, dossier pentest) | No iniciada | H9 | Pendiente |
| F10A-F12A | No iniciada | H10-H12 | Pendiente |
| Oleadas B-E | No iniciadas | - | Pendiente |

**Siguiente acción: una persona aprueba H1 en `docs/APPROVALS.md`.** Sin eso no se construye nada.

## SETUP - detalle

### S0 - Verificación de documentación oficial
- [x] (a) Campos del frontmatter de subagentes
- [x] (b) Alcance de los hooks del frontmatter (y su dependencia del diálogo de confianza)
- [x] (c) JSON del hook por stdin, incluido `agent_type`; convención de bloqueo
- [x] (d) Sintaxis de `permissions` (y que las rutas en `Write(...)` no se consultan)
- [x] (e) Disponibilidad de subagentes nuevos → **requieren reinicio en nuestro caso**
- [x] (f) CLI de plugins
- [x] Registrado en `docs/SETUP_DECISIONS.md` §1

### S1 - Prerrequisitos, repositorio y custodia
- [x] Versiones registradas (falta Docker, Docker Compose y psql)
- [x] `git init` en rama `main`
- [x] `.gitignore`
- [x] `.env.example` (solo nombres)
- [x] Carpetas con `.gitkeep`
- [x] `README.md`
- [x] `docs/APPROVALS.md` (creado antes de bloquearlo)
- [x] `docs/CUSTODY_REGISTER.md` (plantilla vacía)
- [x] `docs/TEST_DATA_POLICY.md`
- [x] `docs/SETUP_DECISIONS.md` y `docs/PROGRESS.md`

### S2 - CLAUDE.md
- [x] `CLAUDE.md` (155 líneas, por debajo del límite de 200)

### S3 - 10 subagentes
- [x] `medical-architect` (opus, docs)
- [x] `clinical-workflow-reviewer` (sonnet, solo lectura)
- [x] `database-architect` (sonnet, db)
- [x] `backend-engineer` (sonnet, backend, worktree)
- [x] `frontend-medical-ux` (sonnet, frontend, worktree)
- [x] `security-privacy-reviewer` (opus, solo lectura)
- [x] `qa-medical` (sonnet, qa)
- [x] `devops-release-engineer` (sonnet, devops)
- [x] `data-migration-reviewer` (sonnet, migration)
- [x] `final-reviewer` (opus, solo lectura)
- [x] Cada escritor con hook `PreToolUse` en su frontmatter
- [x] Hook global de respaldo que identifica al agente por `agent_type`

### S4 - settings.json, hooks y enforcement
- [x] `.claude/settings.json` con `deny` / `ask` / `allow`
- [x] `defaultMode: acceptEdits`, `disableBypassPermissionsMode: disable`
- [x] Hooks globales que aplican también a la sesión principal
- [x] `path_guard.py` (9 dominios, normalización, `PROTECTED_ALL`)
- [x] `bash_guard.py` (perfiles `reviewer` y `dev`)
- [x] `secrets_guard.py`
- [x] `scripts/readonly_scanners.txt` (vacía a propósito)
- [x] Riesgo residual de Bash documentado (`SETUP_DECISIONS.md` §5)

### S5 - 8 skills
- [x] `ipress-peru`
- [x] `clinical-workflows`
- [x] `medical-data-model`
- [x] `healthcare-security`
- [x] `medical-testing`
- [x] `database-migrations`
- [x] `data-migration`
- [x] `release-readiness`

### S6 - Plugins
- [x] `security-guidance` 2.0.8
- [x] `claude-security` 0.12.0
- [x] `feature-dev`
- [x] `frontend-design`
- [x] `.claude/claude-security-guidance.md`
- [x] Sin agente propio `code-explorer` (lo aporta `feature-dev`)

### S7 - Pruebas de violación
- [x] `tests/guards/test_guards.py` (solo biblioteca estándar)
- [x] Casos (a) a (j) exigidos + (k) extra
- [x] **167/167 pasadas** (se corrigieron 3 defectos en los guards, nunca el test)
- [ ] **Pruebas en vivo con cada subagente → PENDIENTE DE REINICIO**
      (procedimiento en `docs/security/agent-boundary-tests.md` §4)
- [ ] **P1 ABIERTO: los hooks globales de `.claude/settings.json` NO se dispararon en la
      sesión que los creó** (probado con `git rev-parse --git-dir`, que debía bloquearse y se
      ejecutó). Verificación obligatoria tras reiniciar en
      `docs/security/agent-boundary-tests.md` §4b
- [x] `docs/security/agent-boundary-tests.md`
- [x] `claude doctor`: sin problemas de instalación
- [ ] **`/doctor` interactivo → PENDIENTE: lo ejecuta una persona tras reiniciar**

### S8 - Borradores de F0
- [x] `docs/PROJECT_GOVERNANCE.md`
- [x] `docs/BUDGET_AND_PROCUREMENT.md`
- [x] `docs/MVP_SCOPE.md`
- [x] `docs/regulatory/NORMATIVE_MATRIX.md` (R1-R17, todo POR VERIFICAR)
- [x] `docs/regulatory/SOURCES_REGISTER.md` (con Q1-Q10 para el asesor)
- [x] `docs/PRIVACY_AND_COMPLIANCE.md`
- [x] `docs/INCIDENT_RESPONSE.md` (48 h marcado POR VALIDAR)
- [x] Plantillas de Discovery F2: `AS_IS_WORKFLOWS`, `SERVICE_CATALOG`, `USER_ROLES`,
      `DATA_INVENTORY`, `CAMPAIGN_OPERATIONS`, `INFRASTRUCTURE_SURVEY`
- [x] `docs/ADR/ADR-TEMPLATE.md` + 9 ADR en estado PROPUESTO

### S9 - Revisión del plan
- [x] `docs/PLAN_REVIEW_v1.2.md` (9 altos, 8 medios, 2 formales; todos ABIERTOS)

### S10 - Bloqueo final
- [x] `deny` de edición sobre `.claude/settings.json`, `.claude/hooks/**`,
      `.claude/agents/**` y `tests/guards/**`
- [x] Procedimiento documentado para levantarlo (`SETUP_DECISIONS.md` §6)
- [x] Verificado: sin secretos, sin datos reales, sin temporales
- [x] Tests reejecutados tras el bloqueo: **167/167**
- [x] Primer commit en `main`

### S11 - Informe y gate H1
- [x] Informe entregado
- [ ] **H1 aprobado en `docs/APPROVALS.md`** ← lo hace una persona

## Pendientes humanos que bloquean el avance

| # | Qué | Rol | Bloquea a |
|---|---|---|---|
| 1 | Aprobar H1 en `docs/APPROVALS.md` | Dirección Médica | Todo |
| 2 | **Reiniciar Claude Code, aceptar la confianza de la carpeta y verificar que los hooks se disparan** (`agent-boundary-tests.md` §4b) | Resp. técnico | **El enforcement por dominio** |
| 2b | Correr las pruebas en vivo de los 10 subagentes | Resp. técnico | Confianza en los límites |
| 3 | Ejecutar `/doctor` en sesión interactiva | Resp. técnico | Validación de configuración |
| 4 | Contratar asesoría legal y revisor independiente | Dirección Médica | **F3** |
| 5 | Completar `docs/CUSTODY_REGISTER.md` (dos administradores por recurso) | Dirección Médica | F4 |
| 6 | Realizar Discovery F2 con las 6 plantillas | Product Owner | **H2** |
| 7 | Verificar R1-R17 en fuente primaria | Asesor legal | **H3** |
| 8 | Responder Q1-Q10 de `SOURCES_REGISTER.md` | Asesor legal | **H3** |
| 9 | Decidir RPO y RTO (ADR-001) | Dirección Médica | F4 |
| 10 | Instalar Docker, Docker Compose y psql | Resp. técnico | F4 |
| 11 | Contratar el certificado de firma digital (plazo largo) | Administración | **F7** |
| 12 | Contratar el pentest externo (agenda escasa) | Dirección Médica | **F9A** |

## Bitácora

| Fecha | Qué se hizo | Resultado |
|---|---|---|
| 2026-10-01 | Bloque SETUP completo (S0-S11) | Completado; detenido en el gate H1 |
