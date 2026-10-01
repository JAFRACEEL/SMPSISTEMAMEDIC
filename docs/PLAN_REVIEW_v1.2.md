# Revisión del Plan Maestro v1.2 - SISTEMAMEDIC

Registro de correcciones propuestas. **Insumo para el Plan v1.3.**
El PDF del Plan v1.2 **no se modifica**: todas las correcciones viven aquí.

Estado inicial de todos los ítems: **ABIERTO**. Los cierra una persona al incorporarlos al
Plan v1.3, anotando quién y cuándo.

Fecha del registro: 2026-10-01.

## Resumen

| Severidad | Nº | Abiertos |
|---|---|---|
| ALTO | 9 | 9 |
| MEDIO | 8 | 8 |
| FORMAL | 2 | 2 |

---

## ALTOS

### A1 - El plan no aprovisiona staging ni PROD
- **Severidad**: ALTO
- **Descripción**: F8A y F9A exigen staging (UAT y pentest externo) y F11A/F12A exigen PROD
  con TLS, dominio, vault y monitoreo, pero ninguna fase del plan los construye ni los
  presupuesta.
- **Corrección propuesta**: añadir la fase **F4b** (aprovisionamiento de staging) y el
  aprovisionamiento de PROD antes de F11A. Documentado en `docs/ADR/ADR-009`.
- **Estado**: ABIERTO

### A2 - F1 se exige tras aprobar F0, pero F1 requiere "Gate F0 alcanzado"
- **Severidad**: ALTO
- **Descripción**: el §27 manda ejecutar F1 tras aprobar solo F0/F1, mientras que F1 declara
  como prerrequisito el gate F0 completo. Dependencia circular que bloquea el arranque.
- **Corrección propuesta**: definir **F1-técnica** (repositorio, política de datos,
  guardrails, entorno de agentes) **no bloqueada** por el resto de F0, y permitir que F2
  (Discovery) corra en paralelo.
- **Estado**: ABIERTO (ya aplicado de hecho en esta ejecución: el gate H1 cubre F0 + F1 técnica)

### A3 - Cronograma inconsistente entre F0, F2 y las demos
- **Severidad**: ALTO
- **Descripción**: F2 (semanas 1-3) arranca con "F0 aprobada", pero F0 ocupa las semanas 1-2.
  Además se prometen demos "desde la semana 8" cuando el primer software funcional aparece en
  F6 (semanas 10-12).
- **Corrección propuesta**: F2 arranca con F1-técnica y con la parte de F0 que no depende de
  Discovery. Demos con **maquetas sintéticas** en las semanas 8-9 y demos **funcionales**
  desde la semana 10.
- **Estado**: ABIERTO

### A4 - Datos "anonimizados" con IA en STAGING/UAT
- **Severidad**: ALTO
- **Descripción**: el §18 permite usar con IA datos "anonimizados formalmente aprobados".
  En una comunidad pequeña como la atendida por esta IPRESS, la **reidentificación es
  probable** (un diagnóstico poco frecuente más una fecha basta).
- **Corrección propuesta**: **con IA, solo datos sintéticos**. La anonimización de datos
  reales la hacen **personas en entorno aislado** y su resultado no se expone a Claude Code.
- **Estado**: ABIERTO (ya aplicado en `docs/TEST_DATA_POLICY.md` y `ADR-004 §D1`)

### A5 - Bash en agentes escritores puede eludir los límites por ruta
- **Severidad**: ALTO
- **Descripción**: un agente con `path_guard` restringido a su dominio puede, vía
  `python script.py` o `npm run x`, ejecutar código que escriba en cualquier parte. El hook
  no inspecciona lo que el script hace por dentro.
- **Corrección propuesta**: allowlist estricta en `bash_guard.py dev`, **rama protegida**,
  **revisión humana del diff** y CI. **Riesgo residual documentado y aceptado**, no eliminado.
- **Estado**: ABIERTO (mitigación implementada; el riesgo residual sigue vivo y está en
  `docs/SETUP_DECISIONS.md`)

### A6 - Falta integridad verificable de la auditoría y política de retención de HCE
- **Severidad**: ALTO
- **Descripción**: el plan exige auditoría pero no define cómo se demuestra que no fue
  alterada. Y no incluye política de retención, archivo y destrucción de la HCE (NTS 139)
  como entregable de F3.
- **Corrección propuesta**: `ADR-006` (hash encadenado + append-only) y `ADR-003 §5`
  (retención) como **entregables obligatorios de F3**.
- **Estado**: ABIERTO

### A7 - "Verificado por: Revisión documental del proyecto" no identifica a nadie
- **Severidad**: ALTO
- **Descripción**: el §3 da por verificadas normas sin nombre, rol ni fecha de quien las
  verificó. Una verificación sin responsable no es una verificación.
- **Corrección propuesta**: exigir **nombre, rol y fecha** en cada fila. **Reverificar R2, R3,
  R6-R11 y R13-R17 antes de F3** contra fuente primaria.
- **Estado**: ABIERTO (`docs/regulatory/NORMATIVE_MATRIX.md` y `SOURCES_REGISTER.md` creados
  con todo en POR VERIFICAR)

### A8 - La regla de 48 h se afirma como firme pero R3 la marca "a validar"
- **Severidad**: ALTO
- **Descripción**: el §22 presenta el plazo de notificación de incidentes de 48 h como
  obligación establecida, mientras la propia matriz normativa lo marca por validar.
  Contradicción interna sobre una obligación legal.
- **Corrección propuesta**: escribir **"POR VALIDAR con asesor"** en ambos lugares hasta
  tener respuesta escrita (pregunta Q1 de `SOURCES_REGISTER.md`).
- **Estado**: ABIERTO (aplicado en `INCIDENT_RESPONSE.md`, `NORMATIVE_MATRIX.md` y la skill
  `healthcare-security`)

### A9 - El modo de permisos exigido es incompatible con la ejecución autónoma
- **Severidad**: ALTO
- **Descripción**: el §10.2 manda usar los modos Plan/Ask, que interrumpen en cada acción.
  Con ellos, la autonomía que el propio plan pide es imposible.
- **Corrección propuesta**: **accept edits** con reglas `allow`/`deny` y **hooks** de
  enforcement real. **Plan mode solo para el diseño** de cada feature. Nunca
  `bypassPermissions`.
- **Estado**: ABIERTO (aplicado en `.claude/settings.json` y en `CLAUDE.md`)

---

## MEDIOS

### M1 - El árbol de archivos del §11 omite documentos clave
- **Severidad**: MEDIO
- **Descripción**: faltan `docs/security/agent-boundary-tests.md`, `PROJECT_GOVERNANCE.md`,
  `BUDGET_AND_PROCUREMENT.md`, `MVP_SCOPE.md`, `TEST_DATA_POLICY.md`, `APPROVALS.md`,
  `CUSTODY_REGISTER.md`, `OPERATIONS_RUNBOOK.md` y todos los documentos de F2.
- **Corrección propuesta**: actualizar el árbol del plan con la estructura real creada.
- **Estado**: ABIERTO

### M2 - Ruta del proyecto incorrecta
- **Severidad**: MEDIO
- **Descripción**: el §10.2 usa `C:\SISTEMAMEDIC`; la raíz real es `C:\SMPSISTEMAMEDIC`.
- **Corrección propuesta**: **parametrizar la ruta**, no fijarla. Los hooks ya resuelven
  contra `CLAUDE_PROJECT_DIR` o el directorio actual, sin rutas absolutas.
- **Estado**: ABIERTO (aplicado en los hooks)

### M3 - Numeración de fases irregular
- **Severidad**: MEDIO
- **Descripción**: 8A-12A, luego 13B, 14C, 15D, 16E. Mezcla número de fase con letra de
  oleada y dificulta referirse a una fase sin ambigüedad.
- **Corrección propuesta**: renombrar por oleada (`A.1`, `A.2`, … `B.1`) o numerar de forma
  secuencial y limpia.
- **Estado**: ABIERTO

### M4 - El límite de `medical-architect` es ambiguo
- **Severidad**: MEDIO
- **Descripción**: "sin implementación salvo aprobación" no se puede traducir a una regla por
  ruta: o puede escribir código o no puede.
- **Corrección propuesta**: **solo `docs/`**, sin excepciones. Si hace falta código, lo
  escribe el agente de ese dominio.
- **Estado**: ABIERTO (aplicado en `.claude/agents/medical-architect.md` y en `path_guard.py`)

### M5 - Idioma/i18n y zona horaria sin definir
- **Severidad**: MEDIO
- **Descripción**: hay campañas internacionales y el plan no dice en qué idioma funciona el
  sistema ni cómo se manejan las zonas horarias.
- **Corrección propuesta**: **ADR-007** (UTC en base, America/Lima en pantalla; español con
  arquitectura preparada para i18n).
- **Estado**: ABIERTO (ADR creado, pendiente de aprobación)

### M6 - Ruta crítica de compras sin fechas límite
- **Severidad**: MEDIO
- **Descripción**: pentest, certificado de firma, revisor independiente y asesoría legal
  tienen plazos de contratación largos y el plan no les pone fecha. Si llegan tarde,
  bloquean fases enteras.
- **Corrección propuesta**: **hitos de contratación** antes de F3 (legal y revisor), antes de
  F5 y F7 (MFA físico y certificado de firma) y antes de F9A (pentest), con fecha límite real.
- **Estado**: ABIERTO (tabla de ruta crítica en `docs/BUDGET_AND_PROCUREMENT.md`, fechas
  PENDIENTE)

### M7 - Las aprobaciones no tienen mecanismo auditable
- **Severidad**: MEDIO
- **Descripción**: el plan habla de gates aprobados sin decir dónde consta la aprobación,
  quién la firmó ni cómo se impide que un agente la dé por hecha.
- **Corrección propuesta**: **`docs/APPROVALS.md`**, escrito solo por una persona, protegido
  por `permissions.deny` y por el hook `path_guard.py` para todos los dominios.
- **Estado**: ABIERTO (aplicado y probado: caso (d) de `tests/guards/test_guards.py`)

### M8 - F7 en 4 semanas con un solo responsable técnico es optimista
- **Severidad**: MEDIO
- **Descripción**: F7 incluye HCE, firma digital, recetas, órdenes, CIE-10, addendum,
  versionado y auditoría íntegra. Es la fase más densa del proyecto.
- **Corrección propuesta**: **buffer de 20-30 %** y, sobre todo, resolver antes la
  dependencia de una sola persona (dos maintainers).
- **Estado**: ABIERTO

---

## FORMALES

### F1 - Formato de fecha inconsistente
- **Severidad**: FORMAL
- **Descripción**: conviven `30/09/2026` y `30 de septiembre de 2026` en el mismo documento.
- **Corrección propuesta**: **`AAAA-MM-DD` en todo documento del proyecto**; `DD/MM/AAAA`
  solo en la interfaz de usuario (ADR-007 §5.3).
- **Estado**: ABIERTO

### F2 - Fuentes no verificadas por el revisor IA
- **Severidad**: FORMAL
- **Descripción**: RM 462-2023, RM 164-2025, RM 188-2026, RM 673-2025, la guía FHIR Perú v0.1,
  la R.S. SUNAT 000075-2026 y la existencia y compatibilidad de los plugins mencionados no
  fueron verificados contra fuente primaria.
- **Corrección propuesta**: verificar cada uno en **fuente primaria**, con nombre, rol y
  fecha, y confirmar además su **vigencia**. Registrado en
  `docs/regulatory/SOURCES_REGISTER.md`.
- **Estado**: ABIERTO (los plugins **sí** se verificaron en esta ejecución; ver
  `docs/SETUP_DECISIONS.md`)

---

## Cierre de ítems

| Ítem | Incorporado al Plan v1.3 por | Fecha | Comentario |
|---|---|---|---|
| | | | |
