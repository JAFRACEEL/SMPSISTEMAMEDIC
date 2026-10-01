# Decisiones de configuración - SISTEMAMEDIC

Registro de lo verificado y lo decidido al montar el entorno. Fase 0-1 técnica.
Fecha de la ejecución: **2026-10-01**.

## 1. Verificación de la documentación oficial (S0)

Consultada en `https://code.claude.com/docs` el **2026-10-01**, para Claude Code **2.1.286**
(nativo, win32-x64, commit f344a08993bb).

**Regla aplicada: cuando la documentación contradice el prompt, gana la documentación.**

### (a) Frontmatter de subagentes

Campos válidos confirmados: `name`, `description` (ambos obligatorios), `tools`,
`disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`,
`memory`, `background`, `omitClaudeMd`, `effort`, `isolation`, `color`, `initialPrompt`,
`experimental`.

- `model` admite `sonnet`, `opus`, `haiku`, `fable`, un ID completo o `inherit`.
- `permissionMode` admite `default`, `acceptEdits`, `auto`, **`dontAsk`**, `bypassPermissions`,
  `plan`, `manual`.
- `isolation` admite `worktree`.
- **Los subagentes de plugin ignoran `hooks`, `mcpServers` y `permissionMode`.** Los nuestros
  son de proyecto, no de plugin, así que sí los usan.

**Diferencia con el prompt**: ninguna. Todos los campos que el prompt pedía existen.

### (b) ¿Los hooks del frontmatter corren solo con ese subagente activo?

**Sí.** La documentación es explícita: *"These hooks only run while that specific subagent is
active and are cleaned up when it finishes."* No afectan a la conversación principal ni a
otros subagentes.

**Pero** hay una condición que el prompt no preveía: los hooks del frontmatter de un
subagente **de proyecto** solo se ejecutan si se **acepta el diálogo de confianza** de la
carpeta. Sin confianza, *"el subagente igual corre, pero Claude Code omite sus hooks de
frontmatter y registra un error en el log de depuración"*.

**Decisión (la más segura)**: se implementan **las dos** vías, no una u otra.
1. Hooks en el frontmatter de cada agente (dominio exacto).
2. **Hook global** en `.claude/settings.json` que corre siempre, lee el campo `agent_type`
   del JSON y aplica el dominio de **ese** agente a través del mapa `AGENT_DOMAINS` de
   `path_guard.py`, **ignorando** el argumento recibido.

Así, si los hooks de frontmatter no se cargan, el enforcement sigue en pie. Verificado en el
caso (k) del test: con argumento `main`, `security-privacy-reviewer` sigue bloqueado.

### (c) JSON que recibe el hook por stdin

Campos confirmados: `session_id`, `prompt_id`, `transcript_path`, `cwd`, `scratchpad_dir`,
`permission_mode`, `effort`, `hook_event_name`, `tool_name`, `tool_input`, `tool_use_id`,
y —**esto era la incógnita**— `agent_id` y **`agent_type`**, presentes solo dentro de un
subagente.

**`agent_type` identifica al subagente por su nombre.** Es lo que hace posible la decisión (b).

Convención de bloqueo confirmada:
- **código 2 + mensaje en stderr = bloqueo incondicional** ← la que usamos.
- código 0 + JSON con `hookSpecificOutput.permissionDecision` = decisión estructurada.
- cualquier otro código = error no bloqueante, la herramienta continúa.

### (d) Sintaxis de `permissions` en `.claude/settings.json`

Confirmada: `allow`, `deny`, `ask`; formato `Tool` o `Tool(especificador)`.
Precedencia: **deny → ask → allow**, por orden; un `allow` **no** puede abrir una excepción a
un `deny`.

**Diferencias importantes con el prompt, corregidas:**

1. **Las reglas de ruta para `Write(...)` y `NotebookEdit(...)` NO se consultan.** Claude Code
   solo evalúa rutas contra `Edit(ruta)` y `Read(ruta)`, y **avisa al arrancar** si se escribe
   una regla de ruta para `Write`, `NotebookEdit`, `Glob` o `MultiEdit`.
   → Todas nuestras reglas de ruta usan `Edit(...)` y `Read(...)`.
2. **Un `Read` deny bloquea también Edit y Write** sobre esa ruta, pero **no** NotebookEdit.
   → Por eso `docs/APPROVALS.md` lleva `Edit(...)` deny y **no** `Read(...)` deny: el motor
   de decisión de este mismo prompt necesita **leer** `APPROVALS.md` para saber qué gate está
   aprobado.
3. **Las rutas en Windows se normalizan a POSIX**: `C:\Users\x` pasa a ser `/c/Users/x`. Para
   una ruta absoluta se usa `//c/...`.
4. Un patrón de un solo segmento como `secrets/**` coincide **a cualquier profundidad** en
   reglas deny/ask, pero solo en la raíz en reglas allow.
5. `Bash(...)` reconoce los operadores de shell: una regla no aprueba `cmd_seguro && otro`.

### (e) ¿Los subagentes nuevos están disponibles de inmediato?

**No en nuestro caso.** La documentación indica tres situaciones que exigen reinicio, y la
primera es exactamente la nuestra: *"crear el primer archivo de agente en un directorio
`agents` nuevo (el vigilante solo cubre los directorios que existían al iniciar la sesión)"*.

→ Los 10 subagentes **no cargan en esta sesión**. Las pruebas en vivo quedan
**PENDIENTE DE REINICIO**, con el procedimiento manual escrito en
`docs/security/agent-boundary-tests.md` §4. Las pruebas automatizadas de los hooks **sí**
corrieron y pasan (167/167).

### (f) CLI de plugins

Confirmado: `claude plugin marketplace add|list|update|remove`, `claude plugin install`,
`enable`, `disable`, `uninstall`, `update`, `list`, `details`, `prune`.
`--scope user|project|local`, `--yes` para scripts.
**No existe** `claude plugin marketplace info` (probado: *unknown command*).

El marketplace oficial `claude-plugins-official` (de `anthropics/claude-plugins-official`)
**ya estaba registrado**, junto con `anthropic-agent-skills`.

## 2. Entorno verificado

| Herramienta | Versión | Nota |
|---|---|---|
| Claude Code | 2.1.286 | nativo |
| Git | 2.53.0.windows.2 | |
| Python | 3.14.4 | disponible como `python` **y** como `py` |
| Node | 24.14.1 | |
| npm | 11.11.0 | |
| Docker | **NO DISPONIBLE** | hace falta para F4 |
| Docker Compose | **NO DISPONIBLE** | hace falta para F4 |
| psql | **NO DISPONIBLE** | hace falta para F4 |

**No se instaló software del sistema.** Docker, Docker Compose y el cliente de PostgreSQL
deben instalarlos una persona antes de F4.

Intérprete de Python elegido para los hooks: **`python`** (comprobado que responde). Si en
otra máquina solo existiera `py`, hay que cambiarlo en `.claude/settings.json` y en el
frontmatter de los agentes.

## 3. Plugins instalados

Instalados a **scope project** (quedan en `.claude/settings.json`, se comparten con el equipo):

| Plugin | Versión | Scope | Estado |
|---|---|---|---|
| `security-guidance@claude-plugins-official` | 2.0.8 | project | habilitado |
| `claude-security@claude-plugins-official` | 0.12.0 | project | habilitado |
| `feature-dev@claude-plugins-official` | ab024cdcfa7c | project | habilitado |
| `frontend-design@claude-plugins-official` | ab024cdcfa7c | project | habilitado |

También presente, a scope user y de antes: `example-skills@anthropic-agent-skills`.

**Compatibilidad con Windows**: los cuatro se instalaron sin error en win32-x64. Su
funcionamiento efectivo se comprobará al usarlos (requiere reinicio para cargar del todo).

**Nota sobre el "explorer"**: el ciclo por feature usa el subagente *explorer* que aporta
`feature-dev`. **No se creó** un agente propio llamado `code-explorer`, como pedía el prompt.

Si hubiera que reinstalarlos a mano, los comandos exactos son:

```
claude plugin marketplace add anthropics/claude-plugins-official
claude plugin install security-guidance@claude-plugins-official --scope project
claude plugin install claude-security@claude-plugins-official --scope project
claude plugin install feature-dev@claude-plugins-official --scope project
claude plugin install frontend-design@claude-plugins-official --scope project
```

Reglas propias de seguridad: `.claude/claude-security-guidance.md` (sin secretos).

## 4. Decisiones tomadas ante ambigüedad (siempre la opción más segura)

| # | Ambigüedad | Decisión | Por qué |
|---|---|---|---|
| 1 | ¿Hooks de frontmatter o hook global? | **Ambos** | El de frontmatter depende del diálogo de confianza; el global no |
| 2 | ¿`Read` deny sobre `docs/APPROVALS.md`? | **No**, solo `Edit` deny | El motor de decisión necesita leerlo para saber qué gate está aprobado |
| 3 | ¿`Write(ruta)` en las reglas? | **No**, solo `Edit(ruta)` y `Read(ruta)` | Las reglas de ruta sobre `Write` no se consultan y generan aviso |
| 4 | `permissionMode` de los revisores | **`dontAsk`** | Deniega sin preguntar; confirmado que existe en esta versión |
| 5 | ¿Permitir `.env.example`? | **Sí** (excepción explícita a `PROTECTED_ALL`) | Es una plantilla sin valores y debe poder actualizarse |
| 6 | Sensibilidad a mayúsculas en las rutas | **Insensible en Windows** (`os.name == "nt"`) | `DOCS\Approvals.MD` debe bloquearse igual que `docs/APPROVALS.md` |
| 7 | `git -c` vs `git switch -c` | Se bloquean **solo las opciones globales antes del subcomando** | `git -c core.pager=touch` ejecuta programas; `git switch -c rama` es legítimo |
| 8 | Marcadores tipo "EXAMPLE" dentro de una clave | **No eximen** a los patrones de alta confianza | `AKIA...EXAMPLE1` tiene forma de clave: se bloquea igual |
| 9 | Scope de instalación de plugins | **project** | Que el equipo tenga la misma configuración |
| 10 | Comandos de inspección de Windows en `bash_guard dev` | Añadidos solo los de **lectura** (`Get-ChildItem`, `Test-Path`…) | Sin ellos la sesión principal no puede inspeccionar nada; ninguno escribe |

## 5. Riesgo residual aceptado

### R-A5: Bash en agentes escritores (hallazgo A5 del Plan v1.2)

**El riesgo**: `bash_guard.py dev` permite `pytest`, `python -m`, `python scripts/…`,
`npm run`, `npx` y `alembic`. El hook inspecciona **la línea de comando**, no lo que el
script hace por dentro. Un script lanzado por cualquiera de esas vías **puede escribir fuera
del dominio del agente**.

**No se puede eliminar** sin impedir que los agentes ejecuten pruebas y migraciones, es decir,
sin impedirles trabajar.

**Compensaciones vigentes**:
1. Rama protegida: nada se trabaja directo en `main`.
2. **Revisión humana del diff** antes de fusionar. Es la compensación principal.
3. CI con lint, tests, escaneo de dependencias y **escaneo de secretos**.
4. `secrets_guard.py` sobre el contenido que se escribe.
5. Agentes de escritura en **worktree aislado** (`backend-engineer`, `frontend-medical-ux`).

**Quién lo acepta**: PENDIENTE - responsable técnico + revisor independiente.

### Otros riesgos en Windows

| # | Riesgo | Mitigación |
|---|---|---|
| 1 | Rutas sensibles a mayúsculas | `path_guard.py` compara en minúsculas cuando `os.name == "nt"`; probado en el caso (j) |
| 2 | Separadores `\` vs `/` | Se normalizan antes de comparar; probado |
| 3 | Rutas largas (> 260 caracteres) | No encontrado aún; vigilar al crear migraciones anidadas |
| 4 | Fin de línea CRLF/LF | PENDIENTE - definir `.gitattributes` en F4 |
| 5 | `python` vs `py` | Se usa `python`, verificado presente. Documentado cómo cambiarlo |
| 6 | Docker no instalado | Bloquea F4; debe instalarlo una persona |
| 7 | La herramienta PowerShell con tuberías está bloqueada por `bash_guard` | Intencional: las tuberías permiten eludir la allowlist. Hay que usar comandos simples |

## 6. Bloqueo final (S10)

Tras terminar la configuración se añadieron a `.claude/settings.json` reglas `deny` sobre la
propia configuración:

```
Edit(.claude/settings.json)
Edit(.claude/hooks/**)
Edit(.claude/agents/**)
Edit(tests/guards/**)
```

(`docs/APPROVALS.md` ya estaba denegado desde el principio.)

### Cómo levantar el bloqueo (lo hace una **persona**, nunca un agente)

1. Abrir `C:\SMPSISTEMAMEDIC\.claude\settings.json` con un editor de texto **fuera de
   Claude Code** (Bloc de notas, VS Code sin la extensión activa).
2. Quitar o comentar temporalmente las reglas `Edit(...)` de la lista anterior que estorben.
3. Hacer el cambio necesario.
4. **Volver a poner las reglas.**
5. Ejecutar `python tests/guards/test_guards.py` y comprobar **167/167**.
6. Anotar aquí qué se cambió, por qué, quién y cuándo.

### Registro de cambios en la configuración bloqueada

| Fecha | Qué se cambió | Por qué | Quién | ¿Tests al 100 % después? |
|---|---|---|---|---|
| | | | | |

## 7. Lo que NO se hizo y por qué

| # | Qué | Por qué |
|---|---|---|
| 1 | Pruebas en vivo con los 10 subagentes | Los agentes creados en un directorio nuevo requieren reiniciar Claude Code (verificado en S0.e). Procedimiento manual en `docs/security/agent-boundary-tests.md` §4 |
| 2 | Agente `code-explorer` | El prompt lo prohíbe expresamente: el *explorer* lo aporta `feature-dev` |
| 3 | Instalar Docker, Docker Compose y psql | El prompt prohíbe instalar software del sistema; solo se registra que faltan |
| 4 | Cualquier escritura en `docs/APPROVALS.md` | Prohibido por diseño; verificado que el bloqueo funciona |
| 5 | Código de aplicación, scaffold o migraciones | Fuera del alcance del gate H1 |
| 6 | `/doctor` interactivo | No es invocable desde una sesión de agente. `claude doctor` (CLI) se ejecutó: *"No installation issues found"*. **PENDIENTE**: una persona debe ejecutar `/doctor` dentro de una sesión interactiva tras reiniciar, para validar la configuración ya cargada |
| 7 | Verificar en vivo los hooks globales | **No fue posible: no se disparan en la sesión que los creó.** Ver §8 |

## 8. Hallazgo abierto (P1): los hooks globales no se dispararon en esta sesión

Prueba realizada el 2026-10-01 en la sesión principal, después de escribir
`.claude/settings.json`:

```
git rev-parse --git-dir     -> se ejecutó y devolvió ".git"
```

`bash_guard.py dev` **debía bloquearlo** (`--git-dir` está en `DANGEROUS_FLAGS`), y lo bloquea
correctamente cuando se le pasa el JSON directamente (caso probado en la suite). Por tanto,
**Claude Code no invocó el hook**.

**Causa más probable**: los hooks de los archivos de configuración se cargan al **iniciar la
sesión**, y `.claude/settings.json` se creó durante esta. Posible factor añadido: la carpeta
no está marcada como de confianza.

**Consecuencia mientras no se verifique**: el enforcement real descansa solo en
`permissions.deny` (que sí cubre `docs/APPROVALS.md`, secretos y comandos destructivos) y
**no** en la separación por dominio entre agentes.

**Qué hacer**: seguir el procedimiento de `docs/security/agent-boundary-tests.md` §4b
**antes** de confiar en los límites y antes de iniciar cualquier fase de construcción.
