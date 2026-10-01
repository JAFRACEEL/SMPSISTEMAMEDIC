# Política de datos de prueba - SISTEMAMEDIC

Versión 1.0 · Vigente desde la Fase 1 técnica · Alcance: todo el equipo, todas las herramientas de IA.

## 1. Regla central

**En DEV y en cualquier herramienta de IA (incluido Claude Code) se usan 100 % datos sintéticos.**

No existe excepción operativa. Si una tarea parece requerir datos reales, se detiene y se escala a la
Dirección Médica y al responsable de privacidad.

## 2. Prohibiciones explícitas

Está prohibido pegar, copiar, subir, transcribir o describir en prompts, código, tests, fixtures,
commits, issues, capturas o documentación:

- Historias clínicas reales o fragmentos de ellas.
- DNI, CE, pasaporte, CPP u otros identificadores reales.
- Nombres, apellidos, direcciones, teléfonos o correos de pacientes o familiares reales.
- Capturas de pantalla de sistemas con datos de pacientes.
- Resultados de laboratorio, imágenes o informes reales.
- Datos de personal con identificadores reales en archivos de prueba.

## 3. Datos sintéticos

- Se generan **por script** (en `scripts/`), de forma reproducible y con semilla documentada.
- DNI ficticios: deben ser evidentemente no válidos y estar fuera de rangos emitidos (se define el
  rango exacto en el generador y se documenta ahí). Nunca se "inventa" un DNI que pueda coincidir con uno real.
- Nombres ficticios: de una lista sintética propia, nunca de personas reales ni de personajes públicos locales.
- Los datos sintéticos **sí** reproducen la complejidad real: pacientes sin documento (NN), menores con
  representante, duplicados, nombres compuestos, tildes y ñ, campañas internacionales, documentos extranjeros.

## 4. Datos reales y anonimización

- La anonimización o seudonimización de datos reales la realizan **únicamente personas autorizadas**, en un
  **entorno aislado**, sin Claude Code ni ninguna otra herramienta de IA conectada.
- El resultado de esa anonimización **no se expone nunca** a Claude Code ni se copia al repositorio.
- Motivo: en una comunidad pequeña como la atendida por la IPRESS, la reidentificación a partir de datos
  "anonimizados formalmente" es probable (ver hallazgo A4 en `docs/PLAN_REVIEW_v1.2.md`).

## 5. Entornos

| Entorno | Datos permitidos | IA permitida |
|---|---|---|
| DEV (local) | Solo sintéticos | Sí |
| CI | Solo sintéticos | Sí |
| STAGING / UAT | Solo sintéticos | Sí, sobre código; **no** sobre datos |
| PROD | Datos reales | **No**. Claude Code no tiene credenciales ni acceso |

## 6. Controles técnicos

- `.gitignore` excluye `data/real/`, volcados (`*.dump`, `*.sqlite`, `*.bak`) y `backups/`.
- El hook `.claude/hooks/secrets_guard.py` bloquea escrituras cuyo contenido parezca credencial o
  combinación de 8 dígitos tipo DNI junto a un nombre en tests/fixtures.
- La CI incluye escaneo de secretos.

## 7. Incumplimiento

Cualquier exposición de datos reales se trata como **incidente de seguridad**: se sigue
`docs/INCIDENT_RESPONSE.md`, se registra y se evalúa el deber de notificación
(DS 016-2024-JUS; el plazo exacto está marcado **POR VALIDAR con asesor**).
