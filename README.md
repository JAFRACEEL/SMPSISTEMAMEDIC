# SISTEMAMEDIC

Sistema integral de atención y gestión clínica para la IPRESS del Centro Médico de la
Parroquia San Martín de Porres, Iquitos.

Referencia: **Plan Maestro v1.2** (borrador en aprobación). Correcciones pendientes en
`docs/PLAN_REVIEW_v1.2.md`.

## Estado

Fase 0-1 técnica: entorno de trabajo, agentes, guardrails y borradores de documentación.
**No hay código de aplicación todavía.** El avance real está en `docs/PROGRESS.md` y las
aprobaciones humanas en `docs/APPROVALS.md`.

## Regla de datos (innegociable)

**100 % datos sintéticos** en desarrollo y en cualquier herramienta de IA. Nunca datos reales
de pacientes en prompts, código, tests, fixtures, commits ni capturas.
Detalle en `docs/TEST_DATA_POLICY.md`.

## Cómo correr las pruebas de guardrails

Desde la raíz del repositorio:

```
python tests/guards/test_guards.py
```

Si `python` no está en el PATH, usa `py tests/guards/test_guards.py`.

Las pruebas usan solo la biblioteca estándar: alimentan los hooks de
`.claude/hooks/` con JSON simulado y verifican que bloqueen lo que deben bloquear.
Deben pasar al 100 %. Si una falla, **se corrige el guard, nunca el test**.

## Documentos clave

| Archivo | Para qué |
|---|---|
| `CLAUDE.md` | Reglas de trabajo para los agentes de IA |
| `docs/APPROVALS.md` | Gates y aprobaciones (**solo lo edita una persona**) |
| `docs/PROGRESS.md` | Checklist de avance por etapa |
| `docs/SETUP_DECISIONS.md` | Decisiones técnicas y verificaciones de documentación |
| `docs/TEST_DATA_POLICY.md` | Política de datos sintéticos |
| `docs/CUSTODY_REGISTER.md` | Custodia de accesos institucionales |
| `docs/security/agent-boundary-tests.md` | Evidencia de que los límites de los agentes funcionan |
| `docs/PLAN_REVIEW_v1.2.md` | Correcciones propuestas al Plan Maestro |

## Aviso

Este repositorio no sustituye validación clínica, legal, tributaria ni de protección de datos.
