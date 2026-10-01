# PROMPT ÚNICO - SISTEMAMEDIC (alineado al Plan Maestro v1.2)

## Antes de pegar (1 minuto)
1. Abre Claude Code dentro de `C:\SMPSISTEMAMEDIC`.
2. Pulsa Shift+Tab hasta ver "accept edits on". NO uses bypass permissions.
3. Pega TODO lo que está debajo de la línea `COPIAR DESDE AQUÍ`.
4. Cuando termine y te informe, tú apruebas en `docs/APPROVALS.md` (Claude no puede escribir ahí) y vuelves a pegar el MISMO prompt: lee su propio estado y sigue con la siguiente fase aprobada. Opcional: añade como primera línea `FASE_OBJETIVO: F5` para forzar una fase (solo corre si su gate está aprobado).

=================== COPIAR DESDE AQUÍ ===================

PROYECTO: SISTEMAMEDIC - sistema integral de atención y gestión clínica para la IPRESS del Centro Médico, Parroquia San Martín de Porres, Iquitos. Referencia: Plan Maestro v1.2 (borrador para aprobación).

# 1. MODO DE TRABAJO (rige todo el prompt)
- AUTONOMÍA TOTAL hasta el próximo gate humano. No me preguntes salvo bloqueo real; ante ambigüedad elige la opción más segura y regístrala en docs/SETUP_DECISIONS.md.
- Este prompt es IDEMPOTENTE y se guía por estado: lee primero docs/PROGRESS.md y docs/APPROVALS.md (si existen). No sobrescribas lo ya hecho; verifica y completa lo que falte.
- Lleva el avance con TodoWrite/TaskCreate y con docs/PROGRESS.md (checklist por etapa/fase, actualizado al terminar cada una). Si la sesión se corta, quien retome lee PROGRESS.md y sigue en el primer ítem sin marcar.
- Mantén el contexto liviano: delega lecturas amplias y revisiones a subagentes; resume en PROGRESS.md.
- Ninguna salida tuya cuenta como aprobación. Solo una persona escribe en docs/APPROVALS.md. Tú nunca lo editas ni marcas un gate como aprobado.
- Nunca: datos reales de pacientes; credenciales o acceso a staging/PROD; bypassPermissions; push forzado; push a main; evadir o editar un hook que te bloquee (reporta y sigue con otra tarea).
- Plataforma: Windows. Raíz = directorio actual (cwd), sin rutas absolutas hardcodeadas. Scripts de hooks y pruebas en Python 3 con pathlib (no bash, no PowerShell); detecta si el intérprete es `python` o `py`. Si el cwd no es repo Git, `git init` (rama main).
- Idioma: español, con tildes y ñ. Respuestas y documentos concisos.

# 2. MOTOR DE DECISIÓN (ejecuta esto primero, siempre)
1. Lee docs/PROGRESS.md y docs/APPROVALS.md. Si no existen o la Etapa S11 no está completa, ejecuta el BLOQUE SETUP (sección 3) y detente en su Gate H1.
2. Si el setup está completo, determina la FASE_OBJETIVO = (la indicada en la primera línea del prompt, si la hay) o, si no, la primera fase de la tabla de la sección 5 cuyo gate previo esté APROBADO (con aprobador y fecha) y que no esté marcada completada en PROGRESS.md.
3. Si el gate previo NO está aprobado: NO construyas. Si H1 está aprobado y H3 no, ejecuta la SÍNTESIS (sección 5, fila "S-DISCOVERY"): consolida lo que los humanos hayan completado en docs/, marca huecos y deja los ADR listos para aprobación. En cualquier otro caso informa qué falta, quién debe aprobarlo y detente.
4. Ejecuta la fase con el CICLO POR FEATURE (sección 4) hasta su punto de parada, entrega el INFORME (sección 6) y detente.

# 3. BLOQUE SETUP (Fase 0-1 técnica; corre solo si el setup no está completo)

## S0 - Verificar documentación oficial (antes de escribir nada)
Consulta https://code.claude.com/docs (agente claude-code-guide o WebFetch) y confirma para la versión instalada:
a) Campos válidos del frontmatter de subagentes (name, description, tools, disallowedTools, model, permissionMode, skills, hooks, isolation...).
b) Si los hooks PreToolUse del frontmatter de un subagente corren solo mientras ese subagente está activo.
c) JSON que recibe el hook por stdin (tool_name, tool_input.file_path, tool_input.command, y si identifica al subagente) y la convención de bloqueo (código 2 + stderr, o JSON de decisión).
d) Sintaxis vigente de permissions.allow/deny/ask en .claude/settings.json (reglas Edit(...), Read(...), Bash(...)).
e) Si los subagentes creados en esta sesión están disponibles de inmediato o requieren reiniciar/recargar.
f) CLI de plugins (claude plugin ...).
Registra lo verificado y toda diferencia con este prompt en docs/SETUP_DECISIONS.md. Si la documentación contradice este prompt, gana la documentación.

## S1 - Prerrequisitos, repositorio y custodia
1. Versiones: claude --version, git, python, node, docker, docker compose, psql. No instales software del sistema; solo registra lo que falte.
2. .gitignore: .env, .env.*, !.env.example, *.pem, *.key, *.pfx, *.p12, secrets/, node_modules/, __pycache__/, .venv/, dist/, build/, *.log, *.sqlite, *.dump, *.bak, backups/, data/real/, .claude/settings.local.json.
3. .env.example (solo nombres de variables, sin valores).
4. Carpetas con .gitkeep: .claude/{agents,skills,rules,hooks}, docs/{ADR,regulatory,security}, backend, frontend, e2e, infra, scripts, tests/guards.
5. README.md corto: propósito, regla de datos sintéticos, cómo correr las pruebas de guardrails.
6. docs/APPROVALS.md (créalo AHORA; después ya no lo tocas): tabla Gate | Alcance | Estado | Aprobador (nombre y rol) | Fecha | Evidencia. Filas: H1 (F0+F1 técnica), H2 (Discovery F2), H3 (ADR F3), H4 (F4+F4b), H5 (F5), H6 (F6), H7 (F7), H8 (F8A), H9 (F9A), H10 (F10A), H11 (F11A), H12 (F12A) y, por cada oleada B-E, UAT/retest/migración/paralelo/go-live. Todas en PENDIENTE. Encabezado: "Este archivo SOLO lo edita una persona. Los agentes de IA no pueden escribirlo."
7. docs/CUSTODY_REGISTER.md: plantilla Recurso | Propietario institucional | Admin 1 | Admin 2 | Recuperación MFA | Fecha, para repositorio, dominio, cuentas cloud/CI, backups, gestor de secretos y certificados. Vacía. Regla: mínimo dos maintainers; nada a nombre de una sola persona.
8. docs/TEST_DATA_POLICY.md: 100% sintéticos en DEV y en cualquier herramienta de IA; prohibido pegar historias, DNI, nombres o capturas reales en prompts, código, tests o commits; datos sintéticos generados por script con DNI/nombres ficticios; la anonimización de datos reales solo la hacen humanos en entorno aislado y nunca es visible a Claude Code.
9. docs/SETUP_DECISIONS.md (contenido real a medida que avanzas) y docs/PROGRESS.md.

## S2 - CLAUDE.md (menos de 200 líneas)
Secciones:
- Propósito, usuarios y entorno (Iquitos: cortes de energía, conectividad irregular, campañas internacionales, pacientes sin DNI, menores, emergencias).
- Reglas innegociables:
  * Una identidad de paciente y una HCE longitudinal; la atención de campaña usa la misma HCE (Encounter con campaign_id opcional). DNI no es obligatorio: patient_identifiers múltiples (DNI, CE, pasaporte, CPP u otros) + identificador interno siempre presente; flujo NN/emergencia y merge auditado.
  * Autorización siempre en backend; ocultar botones no es seguridad.
  * Información clínica cerrada/firmada no se sobrescribe ni elimina; correcciones por addendum/versionado con autor, fecha y motivo.
  * Auditoría de accesos y cambios sensibles con integridad verificable (append-only o hash encadenado, a decidir en ADR). Sin PHI en logs: solo IDs técnicos y correlación.
  * Mínimo privilegio; separar filiación, clínica, caja y administración.
  * Solo datos sintéticos en DEV/IA. Claude Code no tiene credenciales ni acceso a staging/PROD; despliegue solo por CI/CD con aprobación humana. Las migraciones con datos reales las ejecuta una persona autorizada en entorno aislado, sin Claude Code.
  * MFA obligatorio desde F5 para administradores y médicos (TOTP o FIDO2/passkey; SMS no es método principal). Cuentas personales, no compartidas; en PC compartida: bloqueo rápido y reautenticación para acciones sensibles.
  * Break-glass solo con motivo obligatorio, tiempo limitado, alerta y revisión posterior.
  * Cuentas de profesionales visitantes: temporales, con vencimiento, MFA y mínimo privilegio.
  * Tiempo: guardar en UTC, mostrar en America/Lima.
  * La IA no diagnostica, prescribe, da altas ni decide clínicamente.
  * Cumplimiento: Ley 29733 y DS 016-2024-JUS, NTS 139 (RM 214-2018/MINSA), RM 462-2023/MINSA (firma), SIHCE (RM 164-2025, 188-2026, 673-2025), SUNAT/CPE según RUC. Toda afirmación normativa requiere fuente oficial con verificador y fecha; si no, "POR VERIFICAR". Término correcto: EIPD (no DPIA).
- Stack: FastAPI + SQLAlchemy + Alembic + Pydantic; React + TypeScript + Vite + Tailwind; PostgreSQL; Docker Compose; pytest + Playwright; CI con lint, typecheck, tests, build, dependency scan y secret scan.
- Mapa de agentes; el agente principal coordina, no hace todo.
- Ciclo por feature (sección 4 de este prompt) y Definition of Done de 11 dimensiones: funcional, clínica, privacidad, seguridad, datos, pruebas, observabilidad, continuidad, documentación, capacitación, entrega. Todo bug corregido añade un test de regresión.
- Auth, RBAC, break-glass, auditoría e inmutabilidad requieren revisión humana técnica independiente.
- Modo de trabajo: Plan mode solo para diseñar features; implementación en accept edits con allow/deny y hooks; nunca bypassPermissions.
- Dependencia de una persona: runbooks, repositorio y cuentas institucionales; mínimo dos maintainers.
- Aviso: no sustituye validación clínica, legal, tributaria ni de protección de datos.

## S3 - 10 subagentes en .claude/agents/<nombre>.md
Frontmatter (name, description de cuándo usarlo, tools mínimas, model: opus para medical-architect, security-privacy-reviewer y final-reviewer; sonnet para el resto; skills precargadas) + prompt en español con rol, límites y formato de salida (hallazgos con archivo:línea y severidad). Cada agente con escritura lleva un hook PreToolUse en su frontmatter que invoca path_guard.py con su dominio. Si S0 indica que no aplica, usa un hook global que identifique al agente por el campo que provea el JSON y registra el cambio.

| # | Agente | Tools | Escritura permitida (todo lo demás denegado) | Skills |
|---|---|---|---|---|
| 1 | medical-architect | Read, Grep, Glob, Write, Edit | SOLO docs/** (excepto docs/APPROVALS.md). No toca código | ipress-peru, medical-data-model, clinical-workflows |
| 2 | clinical-workflow-reviewer | Read, Grep, Glob | Ninguna; sin Bash | clinical-workflows, ipress-peru |
| 3 | database-architect | Read, Grep, Glob, Write, Edit, Bash(dev) | backend/migrations/**, backend/app/db/**, docs/DATABASE_SCHEMA.md. Migración destructiva exige aprobación humana | medical-data-model, database-migrations |
| 4 | backend-engineer | Read, Grep, Glob, Write, Edit, Bash(dev) | backend/** excepto backend/migrations/** y backend/tests/**. isolation: worktree | healthcare-security, medical-data-model |
| 5 | frontend-medical-ux | Read, Grep, Glob, Write, Edit, Bash(dev) | frontend/src/** y frontend/public/**. isolation: worktree | clinical-workflows, healthcare-security |
| 6 | security-privacy-reviewer | Read, Grep, Glob, Bash(reviewer) | Ninguna. Reporta, no corrige | healthcare-security, ipress-peru |
| 7 | qa-medical | Read, Grep, Glob, Write, Edit, Bash(dev) | backend/tests/**, frontend/tests/**, e2e/**, tests/** (excepto tests/guards/**). Nunca cambia código productivo para pasar un test | medical-testing, clinical-workflows |
| 8 | devops-release-engineer | Read, Grep, Glob, Write, Edit, Bash(dev) | infra/**, .github/**, scripts/** (excepto scripts/migration/**), docker-compose*.yml, Dockerfile*. Sin credenciales; deploy solo por CI con aprobación humana | release-readiness, database-migrations |
| 9 | data-migration-reviewer | Read, Grep, Glob, Write, Edit | docs/DATA_MIGRATION_PLAN.md y scripts/migration/**. Solo esquemas y datos sintéticos; nunca ejecuta migraciones reales | data-migration, medical-data-model |
| 10 | final-reviewer | Read, Grep, Glob, Bash(reviewer) | Ninguna. Clasifica P0/P1/P2 | release-readiness, healthcare-security |

## S4 - settings.json, hooks y enforcement real
.claude/settings.json (sintaxis verificada en S0):
- deny: Read/Edit/Write de .env, .env.*, **/*.pem, **/*.key, **/*.pfx, **/secrets/**, data/real/**; **Edit/Write de docs/APPROVALS.md (desde ya)**; Bash: rm -rf, del /s, format, git push --force, git reset --hard, curl|wget|Invoke-WebRequest hacia ejecución, ssh, scp, kubectl, terraform apply, y cualquier comando contra staging/prod.
- allow: lo necesario en local (git status/diff/log/add/commit/switch en ramas feat/*, python, pytest, npm run, docker compose local).
- Hooks globales PreToolUse que aplican también a la SESIÓN PRINCIPAL (no solo a subagentes): path_guard.py main y bash_guard.py dev.
- No uses ni habilites bypassPermissions.

.claude/hooks/ (Python 3, JSON por stdin, bloqueo con código 2 y mensaje claro en stderr; resuelve rutas contra CLAUDE_PROJECT_DIR o cwd):
- path_guard.py <dominio>: dominios docs, db, backend, frontend, qa, devops, migration, main, none. Para Edit/Write/NotebookEdit normaliza la ruta (.., absolutas, mayúsculas/minúsculas, separadores Windows, symlinks) y permite solo los patrones del dominio. `none` bloquea toda escritura. `main` permite todo el repo excepto las rutas protegidas. Fuera del repo: siempre bloqueado. Protegida para TODOS (incluido main): docs/APPROVALS.md.
- bash_guard.py <perfil>:
  * reviewer: permite SOLO git status, git diff, git log, git show (y escáneres listados en scripts/readonly_scanners.txt, inicialmente vacía). Rechaza pipes, redirecciones (> >>), ;, &, &&, ||, saltos de línea, backticks, $( y flags peligrosos (git -c, --output, --no-index, --exec-path, --git-dir, --work-tree, --ext-diff).
  * dev: allowlist estricta (pytest, python -m, npm run, npx de herramientas del proyecto, alembic, docker compose local, git add/commit/switch/status/diff/log). Rechaza redirecciones, rm/del/mv/cp/tee/sed -i, powershell/cmd /c y la lista deny. Documenta el riesgo residual: un script lanzado por npm/python puede escribir fuera del dominio; compensación = rama protegida, revisión humana del diff y CI.
- secrets_guard.py: bloquea contenido que parezca credencial (claves cloud, tokens, bloque de clave privada, cadenas de conexión con contraseña) o datos reales (8 dígitos de DNI junto a nombre en tests/fixtures).
Enlaza: reviewers -> bash_guard reviewer + path_guard none; escritores -> path_guard <dominio> + bash_guard dev + secrets_guard. En los agentes bloqueados usa el modo de permisos que rechace sin preguntar (dontAsk o equivalente) si S0 lo confirma.

## S5 - 8 skills en .claude/skills/<nombre>/SKILL.md (cada una < 150 líneas)
1. ipress-peru: contexto IPRESS/HCE y matriz normativa (norma | objeto | aplica sí/no/por validar | URL oficial | verificado por nombre y rol | fecha). Precarga R1-R17 del Plan v1.2 §3 como "POR VERIFICAR" con sus URLs; nada pasa a "Verificada" sin verificador humano y fecha. La regla de 48 h de notificación de incidentes (DS 016-2024-JUS art. 34) y sus destinatarios: "POR VALIDAR con asesor". La fecha SUNAT 01/06/2026 no es una regla del sector salud: determinar RUC/régimen.
2. clinical-workflows: máquinas de estado. Cita: scheduled, confirmed, checked_in, waiting, triage, in_care, completed; terminales cancelled, no_show, rescheduled (apunta a la nueva). Laboratorio: ordered, sample_pending, sample_collected, in_process, result_entered, validated, delivered; excepciones sample_rejected, cancelled; posterior amended. Encounter: opened, in_progress, ready_to_sign, signed/closed; posterior addendum. Receta: draft, signed, partially_dispensed, dispensed; terminales cancelled/expired; no dispensar borrador. Campaña: draft, planning, registration_open, confirmed, in_progress, completed; cancelled. Cuenta visitante: invited, verified, active, suspended/expired, closed.
3. medical-data-model: identidad múltiple + identificador interno; NN/emergencia; menores con representante; entidades del plan §15 (patients, patient_identifiers, representatives, consents, privacy_notices, data_subject_requests, allergies, problem_list, encounters, diagnoses, clinical_signatures, signed_documents, addenda, record_versions, icd10_codes, procedure_catalog, payers, coverages, mfa_factors, break_glass_events, audit_events, attachments con checksum); no usar una tabla contenedora "clinical_record".
4. healthcare-security: RBAC/ABAC en backend, IDOR, MFA, sesiones/PC compartidas, break-glass, cuentas visitantes, restricción de acceso desde el exterior, auditoría con integridad verificable, minimización por rol, logs sin PHI, exportaciones auditadas, procedimiento de incidente (plan §22) y gates S1-S13.
5. medical-testing: concurrencia de citas y stock, duplicados/identidad incierta, NN y merge, menores, permisos positivos/negativos, IDOR, inmutabilidad, transiciones inválidas, break-glass, expiración de cuentas visitantes, regresión, resiliencia, migración (conteos/hash).
6. database-migrations: Alembic; no destructivas por defecto; backup + restore probado antes de cambios mayores; rollback; aprobación humana para destructivas.
7. data-migration: decidir por dataset migrar/indexar/digitalizar/conservar en papel; deduplicación; conciliación con conteos; stock solo tras inventario físico; Claude Code solo ve esquemas y datos sintéticos; un humano ejecuta en entorno aislado.
8. release-readiness: checklist por oleada (plan §26), ciclo abreviado B-E (plan §14.1), pentest, paralelo, rollback, evidencias.

## S6 - Plugins
Intenta con el CLI (claude plugin marketplace add anthropics/claude-plugins-official; claude plugin install security-guidance@claude-plugins-official; igual claude-security, feature-dev, frontend-design). Verifica que existan antes. Si el CLI no puede instalarlos desde aquí, NO falles: lista en el informe los comandos /plugin exactos para que yo los ejecute. Registra versión y compatibilidad con Windows en SETUP_DECISIONS.md. Crea .claude/claude-security-guidance.md con reglas propias (RBAC en backend, sin PHI en logs, sin secretos, sin cambios silenciosos en HCE, solo sintéticos, auditoría íntegra); sin secretos. El "explorer" del ciclo es un subagente de feature-dev; no crees un agente propio llamado code-explorer.

## S7 - Pruebas de violación (obligatorias)
1. tests/guards/test_guards.py (solo biblioteca estándar): alimenta los guards con JSON simulado y verifica el código de salida. Casos mínimos: (a) escritura en el dominio propio = permitida; (b) fuera del dominio = bloqueada; (c) ruta con .. o absoluta fuera del repo = bloqueada; (d) escritura en docs/APPROVALS.md por CUALQUIER agente o por la sesión principal = bloqueada; (e) reviewer con git status/diff/log/show = permitido; (f) reviewer con rm, >, |, ;, &&, git -c, --output = bloqueado; (g) dev con rm/del/redirección/powershell = bloqueado; (h) escritura en .env = bloqueada; (i) contenido con clave privada o DNI+nombre en fixtures = bloqueado; (j) mayúsculas/minúsculas y separadores Windows alterados = misma decisión que la ruta canónica.
2. Ejecútalas y corrige el guard (no el test) hasta 100%.
3. Prueba en vivo con cada subagente intentando escribir fuera de su dominio y un reviewer intentando escribir código. Si los agentes nuevos no cargan sin reiniciar, no falles: deja el procedimiento manual y márcalo "PENDIENTE DE REINICIO".
4. docs/security/agent-boundary-tests.md: matriz agente x prueba x resultado x fecha x evidencia (salida real).
5. Ejecuta /doctor o su equivalente CLI y resuelve configuraciones duplicadas o inválidas.

## S8 - Borradores de F0 (sin inventar hechos)
Estructura completa; "PENDIENTE - completa [rol]" donde falte información humana; todo marcado "BORRADOR - requiere aprobación":
- docs/PROJECT_GOVERNANCE.md: roles (Dirección Médica, Product Owner, responsable técnico, revisor técnico independiente, responsable de privacidad/datos o asesor legal, administración/contabilidad, champions por área, pentester externo), RACI por gate, mecanismo APPROVALS.md.
- docs/BUDGET_AND_PROCUREMENT.md: rubros del plan §5.1 (asesoría legal, revisor independiente, pentest, hosting/servidor, UPS/energía/red, PC e impresoras, backups, firma digital/certificados, MFA físico, capacitación) con decisión | responsable | plazo de entrega | fecha límite | costo estimado (vacío). RUTA CRÍTICA: pentest (antes de F9A), certificado de firma (antes de F7), revisor independiente (antes de F3), asesoría legal (antes de F3), hosting/UPS/hardware (antes de F4).
- docs/MVP_SCOPE.md: Oleada A (identidad/pacientes, consentimientos, citas, check-in/cola, triaje, HCE, diagnósticos, recetas, órdenes básicas, firma/cierre) con MUST/SHOULD/LATER y regla de control de alcance.
- docs/regulatory/NORMATIVE_MATRIX.md y SOURCES_REGISTER.md: R1-R17 del plan §3, todos "POR VERIFICAR", con URL, verificador (vacío) y fecha (vacía).
- docs/PRIVACY_AND_COMPLIANCE.md (esqueleto): banco(s) de datos, responsable, deber de informar, bases jurídicas/consentimientos, ARCO, retención/archivo/destrucción de HCE (NTS 139, por validar), contratos con encargados, transferencias internacionales, EIPD (necesidad y metodología), menores, campañas internacionales.
- docs/INCIDENT_RESPONSE.md: los 7 pasos del plan §22 con la regla de 48 h marcada "POR VALIDAR".
- Plantillas de Discovery F2 (no hallazgos), cada una con guion de entrevista por área y tablas vacías: AS_IS_WORKFLOWS.md, SERVICE_CATALOG.md, USER_ROLES.md, DATA_INVENTORY.md, CAMPAIGN_OPERATIONS.md, INFRASTRUCTURE_SURVEY.md.
- docs/ADR/ADR-TEMPLATE.md y borradores (estado PROPUESTO, con opciones y recomendación, NO aprobados, "Decisión: PENDIENTE", aprobador y fecha límite) para: hosting/RPO/RTO/modo degradado; identidad (múltiples identificadores, NN, merge); HCE/firma/addendum/retención; privacidad/EIPD; break-glass; auditoría con integridad verificable; idioma/i18n y zona horaria; almacenamiento de adjuntos; staging y PROD (aprovisionamiento, TLS, dominio, vault).

## S9 - Registro de correcciones del plan: docs/PLAN_REVIEW_v1.2.md
Cada ítem con severidad, descripción, corrección propuesta y estado ABIERTO. Insumo para el Plan v1.3; no modifiques el PDF.
- ALTOS
  - A1. El plan no aprovisiona staging ni PROD, pero F8A/F9A (UAT, pentest) exigen staging y F11A/F12A exigen PROD con TLS, dominio, vault y monitoreo. -> Añadir F4b (staging) y aprovisionamiento de PROD antes de F11A.
  - A2. §27 manda ejecutar F1 tras aprobar solo F0/F1, pero F1 exige "Gate F0 alcanzado". -> Definir F1-técnica (repo, política de datos, guardrails) no bloqueada por el resto de F0; F2 en paralelo.
  - A3. F2 (sem 1-3) arranca con "F0 aprobada" (F0 sem 1-2); demos "desde semana 8" antes de que exista software funcional (F6 sem 10-12). -> Maquetas sintéticas en sem 8-9; demos funcionales desde sem 10.
  - A4. §18: STAGING/UAT permite con IA datos "anonimizados formalmente aprobados"; en una comunidad pequeña la reidentificación es probable. -> Con IA solo sintéticos; anonimizados solo por humanos en entorno aislado.
  - A5. Bash en agentes escritores puede eludir los límites por ruta. -> Allowlist, rama protegida, revisión humana del diff, CI; documentar riesgo residual.
  - A6. Falta integridad verificable de la auditoría y política explícita de retención/archivo/destrucción de HCE (NTS 139) como entregable de F3.
  - A7. §3 "Verificado por: Revisión documental del proyecto" no identifica persona. -> Nombre, rol y fecha; reverificar R2, R3, R6-R11 y R13-R17 antes de F3.
  - A8. §22 afirma la regla de 48 h como firme; R3 la marca "a validar". -> "POR VALIDAR con asesor" en ambos.
  - A9. §10.2 manda Plan/Ask permissions: incompatible con ejecución autónoma. -> accept edits + allow/deny + hooks; Plan mode solo para diseño.
- MEDIOS
  - M1. §11 (árbol) omite docs/security/agent-boundary-tests.md, PROJECT_GOVERNANCE, BUDGET_AND_PROCUREMENT, MVP_SCOPE, TEST_DATA_POLICY, APPROVALS, CUSTODY_REGISTER, OPERATIONS_RUNBOOK y los documentos de F2.
  - M2. §10.2 usa C:\SISTEMAMEDIC; la raíz real es C:\SMPSISTEMAMEDIC. -> Parametrizar.
  - M3. Numeración de fases irregular (8A-12A, 13B, 14C, 15D, 16E). -> Renombrar por oleada o numerar secuencialmente.
  - M4. medical-architect "sin implementación salvo aprobación" es ambiguo frente al guard por ruta. -> Solo docs/.
  - M5. No definidos idioma/i18n para visitantes internacionales ni zona horaria. -> ADR.
  - M6. Ruta crítica de compras con plazos largos sin fechas límite. -> Hitos de contratación antes de F3, F5/F7 y F9A.
  - M7. Aprobaciones sin mecanismo auditable. -> docs/APPROVALS.md escrito solo por humanos.
  - M8. F7 (HCE, firma, recetas, CIE-10) en 4 semanas con un solo responsable técnico es optimista. -> Buffer de 20-30%.
- FORMALES
  - F1. Formato de fecha inconsistente (30/09/2026 vs 30 de septiembre de 2026).
  - F2. No verificado por el revisor IA: RM 462-2023, 164-2025, 188-2026, 673-2025, guía FHIR Perú v0.1, R.S. SUNAT 000075-2026 y los plugins. Verificar con fuente primaria.

## S10 - Bloqueo final y cierre técnico
1. Añade a settings.json deny de edición para .claude/settings.json, .claude/hooks/**, .claude/agents/** (docs/APPROVALS.md ya está denegado), SOLO ahora que ya no los necesitas. Registra en SETUP_DECISIONS.md cómo levantar el bloqueo (lo hace un humano).
2. Verifica que no haya secretos, datos reales ni temporales: git status y búsqueda de patrones.
3. Reejecuta tests/guards/test_guards.py: 100% tras el bloqueo.
4. Marca las etapas en docs/PROGRESS.md y haz el primer commit en main: "chore: entorno Claude Code, agentes, skills, guardrails y borradores F0 (Fase 0-1)".

## S11 - Informe y Gate H1 (aquí te detienes)
Entrega el INFORME (sección 6) y escribe en él qué debo anotar en docs/APPROVALS.md para habilitar H1. DETENTE: no inicies Discovery, scaffold ni código.

# 4. CICLO POR FEATURE (obligatorio en todas las fases de construcción)
- medical-architect (plan + ADR si hace falta) -> clinical-workflow-reviewer (estados) -> database-architect (modelo/migración no destructiva) -> backend-engineer y frontend-medical-ux (en worktrees si van en paralelo; nunca dos escritores sobre los mismos archivos) -> qa-medical (unit, integración, E2E, negativos, concurrencia) -> security-privacy-reviewer (read-only) -> final-reviewer (read-only, P0/P1/P2) -> corrige y repite hasta cero P0/P1 -> documenta.
- Los revisores independientes corren en paralelo.
- Plan mode solo para el diseño de cada feature; implementación en accept edits. Nunca bypass.
- Ramas feat/<tema>; commits pequeños; nada de trabajo directo en main. Push solo si hay remoto configurado y la rama no es main.
- Solo datos sintéticos (generadores en scripts/). Nada de datos reales, credenciales ni acceso a staging/PROD.
- Cada feature cumple la DoD de 11 dimensiones; todo bug añade un test de regresión.
- Al terminar cada feature: commit, actualizar docs/PROGRESS.md y continuar con la siguiente sin parar.

# 5. TABLA DE FASES (alcance autónomo y punto de parada)
| Fase | Requiere | Qué haces solo | Parada |
|---|---|---|---|
| SETUP | nada | Sección 3 completa | H1 |
| S-DISCOVERY | H1 | Consolida lo que los humanos completaron en docs/ (Discovery F2, matriz normativa, presupuesto, custodia), marca huecos y contradicciones, deja ADR listos para aprobación | H2/H3 (humanos) |
| F4 + F4b | H3 | Scaffold FastAPI/SQLAlchemy/Alembic y React/TS/Vite/Tailwind; PostgreSQL y Docker Compose dev; CI (lint, typecheck, tests, build, dependency scan, secret scan); logs sin PHI, health checks, métricas; adjuntos según ADR; script de backup y restore con prueba local y medición contra el RTO; README local; IaC/guías de staging como borrador (sin desplegar) | H4: humano valida restore, CI en el repositorio institucional y provisión real de staging |
| F5 | H4 | Auth, MFA (TOTP/FIDO2), RBAC por servicio, break-glass, cuentas visitantes con vencimiento, registro de profesionales, auditoría de login/elevación, matriz RBAC; tests positivos/negativos/IDOR | H5: revisión humana técnica independiente |
| F6 | H5 | Identidad (múltiples identificadores, NN, menores con representante, merge auditado), consentimientos, agenda/citas/reprogramación/no-show, check-in/cola, triaje; E2E; demos sintéticas para champions | H6: UAT de recepción y triaje |
| F7 | H6 | Encounter, antecedentes, allergies, problem_list, CIE-10 versionado, receta y órdenes básicas, firma/cierre, addendum/versionado, auditoría con integridad verificable, retención según ADR | H7: revisión independiente de auditoría/inmutabilidad y validación de Dirección Médica |
| F8A | H7 | E2E completo sintético, performance con dataset sintético y concurrencia, simulacro de caída/restore/rollback local, release candidate, material de capacitación | H8 |
| F9A-PREP | H8 | Escaneo de dependencias/secretos, hardening TLS/cabeceras/config, revisión de logs, dossier para el pentester externo y lista de remediación (el pentest lo hace un tercero) | H9 |
| F10A-F12A | H9+ | Sin datos reales: solo revisas scripts de migración y runbooks con datos sintéticos. NO ejecutas migración, paralelo ni go-live | humanos |
| OLEADA-B/C/D/E | H12 y oleada previa en hypercare sin bloqueantes | Ciclo abreviado (plan §14.1): build con sintéticos, E2E, material de UAT, revisión de seguridad focal. Migración/configuración, paralelo y go-live son humanos | UAT del área |

Prerrequisito general: el gate previo debe figurar APROBADO en docs/APPROVALS.md con aprobador y fecha, y los ADR que la fase use deben estar APROBADOS. Si no, no construyas.

# 6. INFORME FINAL (al terminar cualquier ejecución, y luego DETENTE)
Entrega en este orden:
a) Qué fase/etapas se ejecutaron y su estado (completada, parcial, bloqueada).
b) Entregables creados o cambiados (árbol resumido).
c) Resultados de pruebas (pasadas/total) y evidencia; pendientes de reinicio.
d) Hallazgos P0/P1/P2 abiertos.
e) En SETUP: matriz agente -> tools -> rutas permitidas/denegadas -> hooks; resumen de settings; plugins instalados/pendientes con versión y comandos manuales; diferencias entre este prompt y la documentación verificada; riesgos en Windows y riesgo residual de Bash.
f) Decisiones y tareas HUMANAS pendientes con responsable y plazo.
g) Qué debo escribir yo en docs/APPROVALS.md para habilitar el siguiente gate y que, al pegar de nuevo este mismo prompt, continúes.

=================== HASTA AQUÍ ===================
