# Propuesta H1: corrección de `path_guard.py` (worktrees + endurecimiento Windows)

**Estado: PROPUESTA (revisión 2). No aplicada. No ejecutada contra el repositorio. H1 NO APROBADO.**
Redactada por Claude Code el 2026-10-01; revisión 2 el mismo día (ver "Revisión 2" al final). Ninguna salida de una IA es una aprobación
(`CLAUDE.md` §9). Toca autenticación/autorización de agentes, por lo que requiere
**revisión humana técnica independiente** (`CLAUDE.md` §8) antes de aplicarse.

## Archivos de esta carpeta

| Archivo | Destino al aplicar | Motivo |
|---|---|---|
| `path_guard.py` | `.claude/hooks/path_guard.py` (reemplaza) | Corrige el bug de worktrees y añade el endurecimiento Windows y la protección de `.git`. Contenido completo final. |
| `test_worktrees.py` | `tests/guards/test_worktrees.py` (archivo **nuevo**) | Casos de regresión nuevos. Autónomo, solo biblioteca estándar. |
| `README.md` | (se queda aquí) | Este documento. |

### Por qué NO hay `test_guards.py` completo

Se pidió `docs/security/proposals/test_guards.py` con el contenido completo. **No se pudo escribir**:
el `test_guards.py` actual contiene literales de prueba con forma de credencial (bloque de clave
privada, clave de AWS, token de GitHub, cadena de conexión con contraseña) y `secrets_guard.py`
bloquea cualquier escritura que los contenga, también dentro de `docs/`. Disfrazar esos literales
(p. ej. concatenando cadenas) sería evadir un hook, prohibido por `CLAUDE.md` §9.

Solución adoptada: **`tests/guards/test_guards.py` no se modifica** (sus 167 casos quedan
intactos byte a byte; verificado con `git diff --stat HEAD -- tests/guards/test_guards.py .claude/hooks`,
salida vacía) y los casos nuevos van en un archivo nuevo, `tests/guards/test_worktrees.py`.
No hace falta ningún patch sobre `test_guards.py`.

### Otros archivos protegidos

- `.claude/settings.json`: **sin cambios**. El hook global sigue invocando `path_guard.py main`.
- `.claude/agents/*.md`: **sin cambios**. Los hooks de frontmatter ya invocan
  `path_guard.py <dominio>` y `isolation: worktree` se mantiene en `backend-engineer` y
  `frontend-medical-ux`.

## Aplicación humana (PowerShell, fuera de Claude Code)

Desde `C:\SMPSISTEMAMEDIC`, en una rama `feat/...` (no en `main`):

```powershell
Copy-Item docs\security\proposals\path_guard.py .claude\hooks\path_guard.py
Copy-Item docs\security\proposals\test_worktrees.py tests\guards\test_worktrees.py
python tests\guards\test_guards.py
python tests\guards\test_worktrees.py
```

Ambos deben terminar con código 0 y `RESULTADO: N/N pasadas`. Si algo falla, **se corrige el
guard, nunca el test**. Las líneas `[OMITIDA]` (symlinks/junctions no disponibles, o variantes
de mayúsculas fuera de Windows) no cuentan como pasadas: anótalas en la evidencia.

Opcional: `docs/security/proposals/__pycache__/` lo generó `py_compile` y ya está ignorado
por `.gitignore`. Se puede borrar a mano.

## Reversión

```powershell
git restore .claude/hooks/path_guard.py
Remove-Item tests\guards\test_worktrees.py
```

(`test_worktrees.py` es un archivo nuevo sin seguimiento, así que `git restore` no lo quita: se borra a mano.)
Después de revertir, `python tests\guards\test_guards.py` debe volver a dar 167/167.

## Riesgo pendiente que la persona revisora debe conocer

**Los subagentes en worktree podrían ejecutar el guard VIEJO.** Si Claude Code fija
`CLAUDE_PROJECT_DIR` al worktree, los hooks de frontmatter
(`${CLAUDE_PROJECT_DIR}/.claude/hooks/path_guard.py`) ejecutan la copia del hook que está
dentro del worktree, que sale del **último commit** de la rama base. Hasta que la corrección
esté commiteada (por una persona) en la rama de la que se crean los worktrees, esos agentes
siguen usando la versión anterior. El hook global de `settings.json` del repo principal sí usa
el archivo nuevo en cuanto se copia. **Hay que verificar en vivo cuál de los dos casos ocurre.**

---

## CAMBIOS DE SEGURIDAD

### Resolución de worktrees

- `repo_context()` resuelve `CLAUDE_PROJECT_DIR` (o el cwd) con `realpath`.
  - Si contiene un **archivo** `.git`, es un worktree. `main_root_from_worktree()` exige todo lo siguiente:
    1. el `.git` tiene exactamente una línea `gitdir: <ruta>`;
    2. esa ruta existe (`resolve(strict=True)`) y es una carpeta `<raíz>/.git/worktrees/<n>`;
    3. `<raíz>/.git` es una carpeta;
    4. el puntero de vuelta `<admin>/gitdir` apunta a **este mismo** `<worktree>/.git`;
    5. el worktree está exactamente en `<raíz>/.claude/worktrees/agent-<hex>` (un solo nivel).

    Si falla cualquiera de los cinco, la raíz es **indeterminada** y toda escritura se **bloquea**.
  - Si no hay archivo `.git` pero la ruta contiene `.claude/worktrees`, también se **bloquea**.
  - En cualquier otro caso se mantiene el comportamiento anterior (la raíz es el directorio del proyecto).
- Las rutas relativas se resuelven contra el directorio del proyecto (la raíz o el worktree). La
  pertenencia se calcula siempre contra la **raíz principal**.
- `classify()` decide cada ruta resuelta:
  - Fuera de `.claude/worktrees/`: se evalúa contra la raíz, **salvo** que contenga un segmento
    `.claude/worktrees` en cualquier otro nivel (worktree falso), que se **bloquea**.
  - En `.claude/worktrees/<n>/...`, `<n>` debe cumplir `agent-<hex>` y su archivo `.git` debe pasar
    la misma validación que `main_root_from_worktree()` y apuntar a **esta** raíz (revisión 2). Se quita **un único** nivel. Si dentro aparece otro
    `.claude/worktrees`, es un worktree anidado y se **bloquea**.
  - Escribir sobre `.claude/worktrees`, sobre `.claude/worktrees/<archivo>` o sobre la carpeta del
    worktree se **bloquea**.
- A la ruta interna del worktree se le aplican las **mismas** reglas de dominio
  (`DOMAIN_ALLOW` y `DOMAIN_DENY`) y las **mismas** `PROTECTED_ALL`. Las rutas protegidas se
  comprueban sobre la ruta interna **y** sobre la ruta completa.

### Canonicalización

Orden fijo **antes** de cualquier regla de autorización:

1. Se rechazan los espacios al inicio o al final de la ruta.
2. Se quitan las comillas exteriores y `\` pasa a `/`.
3. Se aplica `windows_hazard()` (ver más abajo).
4. Regla de `..`.
5. `normpath` léxico y `realpath` (`Path.resolve`).
6. Se calcula la ruta relativa a la raíz principal sin distinguir mayúsculas en Windows.
   Si plegar las mayúsculas cambia la longitud (algunos caracteres Unicode), se **bloquea**.
7. Se clasifica la ruta (raíz o worktree).

Los globs siguen comparándose sin distinguir mayúsculas en Windows. La detección del segmento
`.claude/worktrees` y del nombre `agent-<hex>` no distingue mayúsculas en **ninguna** plataforma,
porque así falla cerrado.

### Protección contra traversal

- Si la ruta contiene `..` y está **dentro** de un worktree (la base es un worktree o la ruta
  incluye un componente `worktrees`), se **bloquea** siempre, aunque el destino final parezca legítimo.
- Fuera de los worktrees se mantiene la regla anterior: la ruta se resuelve y, si queda fuera de
  la raíz, se bloquea.

### Symlinks y junctions

- Se calcula la pertenencia de la ruta léxica (`normpath`) **y** de la ruta real (`realpath`, que
  en Windows sigue symlinks y junctions). Si alguna de las dos cae en un worktree, ambas deben caer
  en el **mismo** worktree. Si no, se **bloquea**.
- Eso cubre:
  - un enlace dentro de un worktree hacia la raíz, hacia otro worktree o hacia fuera del repo;
  - un enlace en la raíz hacia un worktree;
  - una carpeta `agent-<hex>` que en realidad es un junction.
- La decisión final se toma sobre la ruta **real**: un enlace interno que apunta a
  `tests/guards` sigue bloqueado.

### `.git`

- Se añaden `.git`, `.git/**`, `**/.git` y `**/.git/**` a `PROTECTED_ALL`. Cubren:
  - el `.git` del repo principal (incluidos `.git/hooks`, que ejecutan código, y `.git/worktrees/*/gitdir`);
  - el archivo `.git` de cada worktree, cuya manipulación podría redirigir la resolución de la raíz;
  - cualquier repo anidado.
- `.gitignore`, `.gitattributes` y `.github/**` **no** se ven afectados.

### Puntos y espacios finales en Windows

Se bloquea cualquier componente que termine en `.` o en espacio (salvo `.` y `..`), por ejemplo
`APPROVALS.md.`, `APPROVALS.md `, `docs./`, `...` o `.env.`. Win32 recorta esos caracteres y la
escritura caería sobre el archivo protegido. Se aplica también a rutas no protegidas (falla cerrado).

### ADS (Alternate Data Streams)

- Se bloquea cualquier componente que contenga `:`, salvo la letra de unidad de una ruta absoluta
  (`C:/...`). Cubre `::$DATA`, `:stream`, `:stream:$DATA`, `::$INDEX_ALLOCATION` y las rutas
  relativas a unidad (`C:docs/...`).
- También se bloquean otras formas equivalentes:
  - **nombres cortos 8.3** (`~<dígito>`, p. ej. `APPROV~1.MD` o `CLAUDE~1`);
  - **nombres de dispositivo** (`CON`, `PRN`, `AUX`, `NUL`, `COM0-9`, `LPT0-9`, `CONIN$`,
    `CONOUT$`, `CLOCK$`, con o sin extensión);
  - **comodines** y caracteres no válidos (`< > " | ? *`);
  - caracteres de control;
  - **prefijos UNC o de dispositivo** (`\\?\`, `\\.\`, `\\servidor\`).
- Todo esto se evalúa sobre la ruta **tal como llega**, antes de resolverla, y en todas las plataformas.

### Fail-closed

Se bloquea (código 2) en cualquiera de estos casos:

- la raíz no se puede determinar;
- error al resolver la ruta;
- la ruta queda fuera del repo o es la raíz;
- nombre de worktree inválido, worktree sin `.git`, worktree anidado o segmento falso;
- diferencia entre la ruta léxica y la real;
- `..` dentro de un worktree;
- cualquier forma de `windows_hazard`;
- Unicode ambiguo.

Ningún control anterior se quita:

- `DOMAIN_ALLOW`, `DOMAIN_DENY`, `PROTECTED_EXCEPTIONS` y `AGENT_DOMAINS` quedan idénticos.
- `PROTECTED_ALL` solo crece.
- Las herramientas que no escriben siguen sin decisión (código 0). **Cambio (revisión 2):** un JSON
  ilegible, un JSON que no es objeto o una escritura sin ruta ahora se **bloquean** (antes daban 0).

### Lo que sigue SIN cubrir

- **Normalización Unicode**: NTFS no normaliza NFC/NFD, así que no hay alias por esa vía. No se trata.
- **Carrera TOCTOU**: un enlace creado entre la decisión del hook y la escritura de la herramienta.
  El hook no puede impedirlo. Mitigación: los agentes no tienen comandos para crear enlaces
  (`bash_guard`).
- **Hardlinks** a un archivo protegido dentro de un dominio permitido: `realpath` no los detecta.
  Crearlos requiere un comando que `bash_guard` no permite, pero no está probado aquí.
- **Lo que hacen por dentro los scripts** lanzados con `python -m`, `pytest` o `npm run`: riesgo
  residual ya documentado en `bash_guard.py`.
- La **CI** (`.github/workflows/`) todavía no ejecuta `test_worktrees.py`. Añadirlo es tarea de
  `devops-release-engineer` (no protegido) y queda fuera del alcance de esta propuesta.

---

## PRUEBAS NUEVAS

Archivo: `tests/guards/test_worktrees.py`.

- **Recuento estático: 376 verificaciones en Windows** si se pueden crear enlaces. Fuera de
  Windows, las 24 verificaciones de mayúsculas (12 pares) se marcan `[OMITIDA]`.
- **Es un recuento estático, no ejecutado.** El total real lo da la ejecución humana.
- Los casos con worktree usan un repositorio **sintético** en `%TEMP%`, con
  `.git/worktrees/<n>/gitdir` y `commondir` como los crea `git worktree add`. Los worktrees válidos
  son `agent-abc123` y `agent-def456`. **Nunca se escribe en el `.git` real.**
- Notación:
  - `wt/X` = `.claude/worktrees/agent-abc123/X`;
  - "main" = sin `agent_type`, con el argumento `main`;
  - A = PERMITIDA, B = BLOQUEADA.

### (l) Dominio dentro de un worktree (`CLAUDE_PROJECT_DIR` = raíz), 15 casos

1. backend-engineer `wt/backend/app/x.py` A
2. backend-engineer `wt/frontend/src/x.ts` B
3. backend-engineer `wt/backend/tests/x.py` B
4. backend-engineer `wt/backend/migrations/x.py` B
5. frontend-medical-ux `wt/frontend/src/x.ts` A
6. frontend-medical-ux `wt/backend/app/x.py` B
7. frontend-medical-ux `wt/frontend/tests/x.ts` B
8. qa-medical `wt/backend/tests/x.py` A
9. database-architect `wt/backend/migrations/x.py` A
10. medical-architect `wt/docs/nota.md` A
11. devops-release-engineer `wt/.github/workflows/ci.yml` A
12. security-privacy-reviewer `wt/docs/nota.md` B
13. main `wt/README.md` A
14. backend-engineer, ruta absoluta `<raíz>\.claude\worktrees\agent-abc123\backend\app\x.py` A
15. backend-engineer, ruta absoluta `...\agent-abc123\frontend\src\x.ts` B

### (m) Rutas protegidas dentro del worktree, 100 casos

- 99 casos: cada uno de los 10 agentes (medical-architect, clinical-workflow-reviewer,
  database-architect, backend-engineer, frontend-medical-ux, security-privacy-reviewer, qa-medical,
  devops-release-engineer, data-migration-reviewer, final-reviewer) **y** main (11 en total), contra
  cada una de estas 9 rutas, **todas B**:
  - `wt/docs/APPROVALS.md`
  - `wt/.claude/hooks/path_guard.py`
  - `wt/.claude/settings.json`
  - `wt/.claude/agents/x.md`
  - `wt/tests/guards/x.py`
  - `wt/.env`
  - `wt/backend/.env.local`
  - `wt/.git`
  - `wt/secrets/x.json`
- 100. main `wt/.env.example` A (no regresión de la excepción).

### (n) Escapes con `..`, 14 casos

Cada ruta con main **y** con backend-engineer, **todas B**:

1. `wt/../../settings.json`
2. `wt/../agent-def456/backend/app/x.py`
3. `wt/backend/../backend/app/x.py`
4. `wt/../../../backend/app/x.py`
5. `.claude\worktrees\agent-abc123\..\..\settings.json`
6. `<raíz absoluta>\.claude\worktrees\agent-abc123/../../settings.json`
7. `backend/../.claude/worktrees/agent-abc123/backend/app/x.py`

### (o) Nombre de worktree inválido, 15 casos

- 12 casos: cada nombre (registrado con un `.git` válido, de modo que solo falla el nombre) con
  main **y** con backend-engineer, ruta `.claude/worktrees/<nombre>/backend/app/x.py`, **todas B**.
  Nombres: `otro`, `agent-xyz`, `agent-`, `agent-abc123x`, `xagent-abc123`, `agent_abc123`.
- 13. main `.claude/worktrees/nuevo.txt` B
- 14. main `.claude/worktrees/agent-abc123` (la carpeta del worktree) B
- 15. main `.claude/worktrees` B

### (p) Worktree sin `.git`, 3 casos

1. main `.claude/worktrees/agent-0bad00/backend/app/x.py` (carpeta existente, sin `.git`) B
2. backend-engineer, la misma ruta B
3. backend-engineer `.claude/worktrees/agent-0bad99/backend/app/x.py` (no existe) B

### (q) Worktree anidado o falso, 12 casos

Existe un worktree anidado registrado en `wt/.claude/worktrees/agent-def789`. Cada ruta con main
**y** con backend-engineer, **todas B**:

1. `wt/.claude/worktrees/agent-def789/backend/app/x.py`
2. `wt/.claude/worktrees/agent-def789/README.md`
3. `wt/.claude/worktrees/agent-123abc/README.md`
4. `wt/backend/.claude/worktrees/agent-def789/x.py`
5. `backend/.claude/worktrees/agent-abc123/x.py`
6. `docs/.claude/worktrees/agent-abc123/nota.md`

### (r) `.git`, 27 casos

- 21 casos: cada ruta con main, devops-release-engineer **y** backend-engineer, **todas B**:
  - `.git`
  - `.git/config`
  - `.git/hooks/pre-commit`
  - `.git/worktrees/agent-abc123/gitdir`
  - `backend/.git/config`
  - `wt/.git`
  - `wt/backend/.git/hooks/post-checkout`
- 22. main, ruta absoluta `<raíz>\.git\config` B
- 23. main `.git/config` sobre el **repo real** (solo se evalúa el JSON, no se escribe nada) B
- 24. main `.git/hooks/pre-commit` sobre el repo real B
- 25. main `.gitignore` A
- 26. main `.gitattributes` A
- 27. devops-release-engineer `.github/workflows/ci.yml` A

### (s) `CLAUDE_PROJECT_DIR` = worktree, 60 casos

48 casos: cada fila se prueba de 4 formas:

1. con la raíz como proyecto, ruta relativa;
2. con la raíz como proyecto, ruta `wt/X`;
3. con el worktree como proyecto, ruta relativa;
4. con el worktree como proyecto, ruta absoluta dentro del worktree.

Las 4 formas deben dar la misma decisión:

| Agente | Ruta | Esperado |
|---|---|---|
| backend-engineer | `backend/app/x.py` | A |
| backend-engineer | `frontend/src/x.ts` | B |
| backend-engineer | `backend/tests/x.py` | B |
| backend-engineer | `backend/migrations/x.py` | B |
| frontend-medical-ux | `frontend/src/x.ts` | A |
| frontend-medical-ux | `backend/app/x.py` | B |
| security-privacy-reviewer | `docs/nota.md` | B |
| main | `README.md` | A |
| main | `docs/APPROVALS.md` | B |
| main | `.claude/hooks/path_guard.py` | B |
| main | `.claude/settings.json` | B |
| main | `tests/guards/x.py` | B |
| main | `.env` | B |
| main | `.git` | B |

Más 4 casos con el worktree como proyecto:

- backend-engineer, ruta absoluta a `<raíz>\backend\app\x.py` A
- main, ruta absoluta a `<raíz>\docs\APPROVALS.md` B
- backend-engineer `../../../backend/app/x.py` B
- main `../../settings.json` B

### (s2) Raíz no determinable, 18 casos

Cada proyecto de esta lista con main → `README.md` **y** con backend-engineer → `backend/app/x.py`,
**todas B**:

1. `.claude/worktrees/agent-0bad10` sin `.git`
2. `agent-0bad11` con un `.git` de contenido basura
3. `agent-0bad12` con un `gitdir` que no existe
4. `agent-0bad13` cuyo puntero de vuelta apunta a otro worktree
5. `otros/agent-0bad14`, registrado pero fuera de `.claude/worktrees`
6. `agent-0bad15` con `gitdir` = `<raíz>/.git` (no está en `.git/worktrees`)
7. `.claude/worktrees/otro-wt`, registrado pero con nombre inválido
8. `agent-0bad16` con un `.git` de dos líneas
9. `wt/.claude/worktrees/agent-0bad17`, anidado y registrado

### (t) Variantes de mayúsculas y separadores, 34 casos

Cada par = canónica + variante (2 casos), con la misma decisión.

Separadores, en todas las plataformas (5 pares, 10 casos):

1. backend-engineer `wt/backend/app/x.py` frente a `.claude\worktrees\agent-abc123\backend\app\x.py` A
2. backend-engineer `wt/frontend/src/x.ts` frente a la misma ruta con `\` B
3. main `wt/docs/APPROVALS.md` frente a la misma ruta con `\` B
4. main `wt/.claude/hooks/path_guard.py` frente a `.claude/worktrees\agent-abc123/.claude\hooks/path_guard.py` (separadores mezclados) B
5. backend-engineer, ruta absoluta con `/` frente a la misma con `\` A

Mayúsculas, solo en Windows (12 pares, 24 casos; fuera de Windows quedan `[OMITIDA]`):

6. backend-engineer `.CLAUDE/WORKTREES/AGENT-ABC123/BACKEND/APP/x.py` A
7. backend-engineer `.Claude\Worktrees\Agent-Abc123\Backend\App\X.PY` A
8. backend-engineer `.CLAUDE\worktrees\agent-ABC123\BACKEND\TESTS\x.py` B
9. frontend-medical-ux `.claude/WORKTREES/agent-abc123/FRONTEND/SRC/X.TS` A
10. main `.claude/worktrees/AGENT-abc123/DOCS/approvals.md` B
11. main `.claude\worktrees\agent-abc123\.CLAUDE\HOOKS\PATH_GUARD.PY` B
12. main `.claude/worktrees/agent-abc123/.Claude/Settings.JSON` B
13. main `.claude/worktrees/agent-abc123/TESTS/GUARDS/x.py` B
14. main `.GIT\CONFIG` B
15. main `.claude/worktrees/agent-abc123/.GIT` B
16. backend-engineer, ruta absoluta del worktree **en minúsculas** A
17. backend-engineer, ruta absoluta del worktree **en mayúsculas** A

### (u) Endurecimiento Windows, 60 casos

Con main sobre el repo real (solo JSON), 46 casos, **todos B**. `<APR>` = ruta absoluta de
`docs/APPROVALS.md` en el repo real.

- **Punto o espacio final:**
  - `docs/APPROVALS.md.`
  - `docs/APPROVALS.md ` (espacio final)
  - `docs/APPROVALS.md...`
  - `docs/APPROVALS.md. .`
  - `docs./APPROVALS.md`
  - `docs /APPROVALS.md`
  - `docs\APPROVALS.md.`
  - `.env.`
  - `.env ` (espacio final)
  - `.claude/settings.json.`
  - `.claude./hooks/path_guard.py`
  - `.claude/hooks./path_guard.py`
  - `tests/guards./x.py`
  - `.git./config`
  - `...`
- **ADS y rutas relativas a unidad:**
  - `docs/APPROVALS.md::$DATA`
  - `docs/APPROVALS.md:$DATA`
  - `docs/APPROVALS.md:oculto`
  - `docs/APPROVALS.md:oculto:$DATA`
  - `docs\APPROVALS.md::$DATA`
  - `DOCS\approvals.md::$data`
  - `.env::$DATA`
  - `.claude/hooks/path_guard.py::$DATA`
  - `.claude/settings.json:x`
  - `docs::$INDEX_ALLOCATION/APPROVALS.md`
  - `.git::$INDEX_ALLOCATION/config`
  - `C:docs/APPROVALS.md`
  - `<APR>::$DATA`
  - `<APR>.`
- **Nombres cortos 8.3:**
  - `DOCS~1/APPROVALS.md`
  - `docs/APPROV~1.MD`
  - `CLAUDE~1/hooks/path_guard.py`
  - `.claude/SETTIN~1.JSO`
- **Nombres de dispositivo:**
  - `docs/CON`
  - `docs/nul.md`
  - `docs/COM1.txt`
  - `docs/LPT1`
  - `AUX`
- **Prefijos UNC o de dispositivo:**
  - `\\?\<APR>`
  - `\\.\<APR>`
  - `\\?\UNC\localhost\c$\x.md`
  - `//localhost/c$/x.md`
- **Comodines:**
  - `docs/APPRO*.md`
  - `docs/APPROVALS.m?`
  - `docs/<x>.md`
- **Espacio inicial:** ` docs/APPROVALS.md`

Rutas **no protegidas** con el dominio docs, 5 casos, **todos B**:

- `docs/nota.md:stream`
- `docs/nota.md.`
- `docs/nota.md ` (espacio final)
- ` docs/nota.md` (espacio inicial)
- `docs/NOTA~1.MD`

Dentro de un worktree, 9 casos, **todos B**:

- backend-engineer `wt/backend/app/x.py.`
- backend-engineer `wt/backend/app/x.py::$DATA`
- backend-engineer `wt/backend/app/x.py ` (espacio final)
- backend-engineer `wt/backend/tests./x.py`
- main `wt/docs/APPROVALS.md.`
- main `wt/docs/APPROVALS.md::$DATA`
- main `wt/.claude/hooks/path_guard.py.`
- main `.claude/worktrees/agent-abc123./backend/app/x.py`
- main `.claude/worktrees/agent-abc123::$INDEX_ALLOCATION/README.md`

### (u2) No regresión del endurecimiento, 9 casos, **todos A**

1. docs `docs/v1.2/nota.md`
2. docs `docs/nota.v2.md`
3. docs `docs/.nota.md`
4. docs `docs/a b/nota.md`
5. docs `./docs/nota.md`
6. docs, ruta absoluta `<raíz real>\docs\NOTA.md`
7. main `.env.example`
8. main `README.md`
9. devops `docker-compose.dev.yml`

### (v) Symlinks y junctions, 9 casos

Se prueba `os.symlink` y, en Windows, `_winapi.CreateJunction`. Si ninguno funciona, el caso se
marca `[OMITIDA]` y no cuenta.

1. Enlace `wt/backend/app/esc` → `<raíz>/backend/app`; backend-engineer `wt/backend/app/esc/x.py` B
2. Enlace `wt/backend/app/fuera` → carpeta temporal fuera del repo; backend-engineer `wt/backend/app/fuera/x.py` B
3. Enlace `<raíz>/backend/app/hacia_wt` → `wt/backend/app`; backend-engineer `backend/app/hacia_wt/x.py` B
4. Enlace `wt/backend/app/otro` → `agent-def456/backend/app`; backend-engineer `wt/backend/app/otro/x.py` B
5. Carpeta `.claude/worktrees/agent-fff000` enlazada a la raíz; main `.claude/worktrees/agent-fff000/backend/app/x.py` B
6. Enlace `wt/docs/enlace` → `<raíz>/docs`; main `wt/docs/enlace/APPROVALS.md` B
7. Enlace `wt/backend/app/aguards` → `wt/tests/guards`; backend-engineer `wt/backend/app/aguards/x.py` B
8. Enlace `<raíz>/docs/fuera` → carpeta temporal fuera del repo; medical-architect `docs/fuera/nota.md` B
9. Enlace `wt/backend/app/interno` → `wt/backend/app/sub` (mismo worktree); backend-engineer `wt/backend/app/interno/x.py` A (no regresión)

### (w1) Raíz real con "~1" en su nombre, 10 casos (revisión 2)

Segundo repo sintético en `%TEMP%\smp~1_raiz_*`, con su worktree `agent-abc123` registrado.
`<R>` = esa raíz y `<W>` = su worktree.

1. main, `<R>\docs\nota.md` (absoluta) A
2. backend-engineer, `<R>\backend\app\x.py` (absoluta) A
3. main, `docs/nota.md` (relativa) A
4. main, `<R>\docs\APPROVALS.md` B
5. main, `<R>\docs\NOTA~1.MD` B (el "~1" bajo la raíz sí se bloquea)
6. main, `<R>\docs\nota.md.` B
7. backend-engineer, `<W>\backend\app\x.py` (absoluta) A
8. backend-engineer, con el proyecto en `<W>`, `backend/app/x.py` A
9. backend-engineer, con el proyecto en `<W>`, `<W>\backend\app\x.py` A
10. main, `<R>\docs\nota.md` en MAYÚSCULAS A (solo Windows; fuera de Windows queda `[OMITIDA]`)

### (w2) Nombres de dispositivo en el frontend, 9 casos (revisión 2)

frontend-medical-ux:

1. `frontend/src/Con.tsx` B
2. `frontend/src/components/con.tsx` B
3. `frontend/src/CON.TSX` B
4. `frontend/src/Nul.tsx` B
5. `frontend/src/Aux.ts` B
6. `frontend/src/Console.tsx` A
7. `frontend/src/Contacto.tsx` A
8. `frontend/src/Auxiliar.tsx` A
9. `wt/frontend/src/Con.tsx` B

### (w3) Payload de escritura sin ruta o ilegible, 14 casos (revisión 2)

1. Write sin `file_path` B
2. Write sin `file_path`, con agent_type backend-engineer B
3. Edit sin `file_path` B
4. NotebookEdit sin `notebook_path` B
5. MultiEdit con `edits: []` B
6. Write con `file_path: ""` B
7. Write con `file_path: 123` B
8. Write con `tool_input` de tipo texto B
9. Write sin `tool_input` B
10. stdin con JSON ilegible B
11. stdin vacío B
12. stdin con JSON que no es objeto (lista) B
13. Read sin ruta A (no regresión: no es herramienta de escritura)
14. Bash `git status` A (no regresión)

### (w4) Worktree falso con `.git` inválido, 10 casos (revisión 2)

Cada worktree, con main **y** con backend-engineer, ruta `.claude/worktrees/<n>/backend/app/x.py`,
**todas B**:

1. `agent-0bad20`: `.git` con contenido basura
2. `agent-0bad21`: `.git` que apunta al admin de `agent-abc123` (el puntero de vuelta no coincide)
3. `agent-0bad22`: registrado en **otro** repositorio sintético
4. `agent-0bad23`: `.git` como carpeta (ya no se acepta)
5. `agent-0bad24`: `.git` de dos líneas

### Total

15 + 100 + 14 + 15 + 3 + 12 + 27 + 60 + 18 + 34 + 60 + 9 + 9 + 10 + 9 + 14 + 10 = **419**
verificaciones nuevas (recuento estático), además de las **167 existentes** de `test_guards.py`,
que no cambian. Fuera de Windows, 13 se marcan `[OMITIDA]`.

## Revisión 2 (cambios sobre la primera propuesta)

1. **Fail-closed en la entrada.** Verificado que el `matcher` del hook es solo de escritura
   (`Edit|Write|NotebookEdit|MultiEdit`) en `.claude/settings.json` y en los 10
   `.claude/agents/*.md`. Por tanto ahora se **bloquean**:
   - un JSON ilegible;
   - un JSON que no es objeto;
   - una herramienta de escritura sin ruta reconocible.

   `targets_from()` ya no falla con un `tool_input` que no es objeto. Antes lanzaba una
   excepción, el hook terminaba con código 1 y Claude Code lo trata como error **no bloqueante**:
   era una vía para saltarse el guard. Las herramientas que no escriben siguen dando código 0.
2. **`windows_hazard` solo bajo la raíz.** En rutas absolutas se quitan los componentes iniciales
   que coinciden exactamente (sin mayúsculas en Windows) con la raíz principal o con la base del
   proyecto, ya resueltas; se usa la más larga. Así una raíz que contenga `~1` u otro nombre
   rechazable no bloquea todo el repo. Si la ruta no empieza exactamente por la raíz (alias 8.3,
   UNC, otra unidad), se evalúa **completa** y falla cerrado. Las rutas relativas se evalúan completas.
3. **Worktree verificado de verdad.** `classify()` ya no se conforma con que exista `.git`: exige que
   `main_root_from_worktree(wt_dir)` devuelva exactamente la raíz principal. Un `.git` basura,
   apuntando a otro worktree, registrado en otro repo, de varias líneas o **como carpeta** = BLOQUEADO.
   Esto **corrige** lo que decía la primera versión ("`.git` archivo o carpeta").

## Verificación hecha por Claude Code

- `python -m py_compile docs/security/proposals/path_guard.py docs/security/proposals/test_worktrees.py`:
  **sin errores** (solo sintaxis).
- **No** se ejecutaron las pruebas, ni contra el repo ni contra la propuesta, según la instrucción
  recibida. No hay resultados reales de aprobado/fallido.
