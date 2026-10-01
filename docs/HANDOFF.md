# Handoff - SISTEMAMEDIC

**Fecha: 2026-10-01.** Para quien retome, sea una persona o una nueva sesión de Claude Code.
Léelo junto con `docs/PROGRESS.md` (estado general) y `docs/APPROVALS.md` (gates).

## Dónde estamos

- **Fase:** SETUP (F0 + F1 técnica) completada. Detenidos en el **gate H1, que NO está aprobado**.
- **Rama:** `main`. No hay commits nuevos desde `117e777`.
- **Bloqueante abierto, P1:** `path_guard.py` rechaza toda escritura dentro de un worktree
  (`.claude/worktrees/agent-<hex>/...`). Por eso `backend-engineer` y `frontend-medical-ux`
  (`isolation: worktree`) no pueden escribir ni en su propio dominio. La evidencia está en
  `docs/security/agent-boundary-tests.md` §4, ronda 2.

## Qué se hizo en esta sesión

1. Claude Code intentó corregir `.claude/hooks/path_guard.py` y **el propio hook lo bloqueó**:
   `.claude/hooks/**` está en `PROTECTED_ALL`, así que el bloqueo S10 funciona. **No se evadió.**
2. Por indicación del usuario (opción A, edición humana), la corrección se dejó como
   **propuesta** en `docs/security/proposals/`:

   | Archivo | Destino | Contenido |
   |---|---|---|
   | `path_guard.py` | `.claude/hooks/path_guard.py` | Guard completo, revisión 2 |
   | `test_worktrees.py` | `tests/guards/test_worktrees.py` (nuevo) | 419 casos nuevos (recuento estático) |
   | `README.md` | se queda | CAMBIOS DE SEGURIDAD, PRUEBAS NUEVAS, aplicación, reversión y riesgos |

3. Lo que cubre la revisión 2:
   - resolución de worktrees, validando `gitdir` y el puntero de vuelta;
   - `CLAUDE_PROJECT_DIR` apuntando a un worktree;
   - bloqueo de `..` en worktrees, de worktrees anidados o falsos y de escapes por symlink o junction
     (comparando `normpath` con `realpath`);
   - protección de `.git`;
   - endurecimiento Windows: punto o espacio final, ADS (`:`), nombres cortos 8.3, nombres de
     dispositivo (incluido `Con.tsx`), UNC y comodines, evaluado solo en el tramo bajo la raíz;
   - *fail-closed* ante JSON ilegible o escrituras sin ruta;
   - `classify()` exige que el `.git` del worktree apunte a esta raíz.
4. **`tests/guards/test_guards.py` no se toca.** Sus 167 casos siguen idénticos
   (`git diff --stat HEAD` vacío). No se pudo copiar a `proposals/` porque contiene literales de prueba con
   forma de credencial y `secrets_guard` lo bloquea. Por eso los casos nuevos van en un archivo aparte.
5. Verificación hecha: **solo** `python -m py_compile` sobre las dos propuestas, sin errores.
   **Las pruebas NO se ejecutaron**, por instrucción del usuario.
6. Documentos sincronizados: `docs/PROGRESS.md` (checklist, pendientes y bitácora) y
   `docs/security/agent-boundary-tests.md` (estado del hallazgo).

## Siguiente paso: solo personas

Desde `C:\SMPSISTEMAMEDIC`, en una rama `feat/path-guard-worktrees` (no en `main`):

```powershell
# 1. Revisión humana técnica independiente del diff (CLAUDE.md §8)
git diff --no-index .claude\hooks\path_guard.py docs\security\proposals\path_guard.py

# 2. Aplicar
Copy-Item docs\security\proposals\path_guard.py .claude\hooks\path_guard.py
Copy-Item docs\security\proposals\test_worktrees.py tests\guards\test_worktrees.py

# 3. Probar: ambas al 100 %; si falla algo se corrige el guard, nunca el test
python tests\guards\test_guards.py
python tests\guards\test_worktrees.py

# Revertir si hace falta
git restore .claude/hooks/path_guard.py
Remove-Item tests\guards\test_worktrees.py
```

Después:

1. Commit humano en la rama. Hasta ese commit, los agentes en worktree siguen ejecutando el
   guard del último commit.
2. Repetir la ronda 2 en vivo con `backend-engineer` y `frontend-medical-ux`.
3. Añadir `test_worktrees.py` a la CI (`devops-release-engineer`).
4. Aprobar H1 en `docs/APPROVALS.md` (Dirección Médica).

## Restricciones vigentes (del usuario)

- No modificar rutas protegidas: `.claude/hooks/**`, `.claude/settings.json`,
  `.claude/agents/**`, `tests/guards/**`, `docs/APPROVALS.md`, `.env*`, `.git/**`.
- No desactivar hooks, no usar bypass, no hacer commit sin que lo pidan, no hacer push.
- **No avanzar a Discovery/F2.** **No declarar H1 listo.**
- No ejecutar las pruebas contra el repo sin autorización explícita (solo `py_compile`).
  Ejecutar la suite propuesta contra el guard propuesto, usando solo `%TEMP%`, quedó **ofrecido y sin respuesta**.

## Riesgos y temas abiertos

- **Sin cubrir por la propuesta:** carrera TOCTOU (entre la decisión del hook y la escritura),
  hardlinks, y lo que hacen por dentro los scripts lanzados con `python -m`, `pytest` o `npm run` (riesgo A5).
- `.claude/settings.json` aparece como modificado en el working tree desde **antes** de esta sesión.
  No lo tocó Claude Code. Una persona debe revisarlo.
- `docs/security/proposals/__pycache__/` lo generó `py_compile`. Está ignorado por `.gitignore` y se puede borrar a mano.
- `%TEMP%\path_guard.diff` está en UTF-16. Para regenerarlo en UTF-8:
  `git diff --no-index .claude\hooks\path_guard.py docs\security\proposals\path_guard.py | Out-File -Encoding utf8 $env:TEMP\path_guard.diff`
  Ojo: ese diff es anterior a la revisión 2, así que conviene regenerarlo.
- La memoria persistente de Claude Code (`~/.claude/projects/.../memory/`) **no se pudo guardar**:
  `path_guard` bloquea toda escritura fuera del repo. Es correcto que lo haga, así que el único
  traspaso es este archivo. Si se quiere usar esa memoria, hay que decidir si `path_guard` debe
  permitir esa ruta (cambio en un archivo protegido, lo hace una persona).
- Siguen pendientes los ítems humanos de `docs/PROGRESS.md` (custodia, asesor legal, Docker, etc.).

**PROPUESTA LISTA PARA REVISIÓN HUMANA. H1 NO APROBADO.**
