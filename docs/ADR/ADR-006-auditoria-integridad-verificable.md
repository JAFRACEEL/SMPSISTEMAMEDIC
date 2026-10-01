# ADR-006: Auditoría con integridad verificable

- **Estado**: PROPUESTO
- **Decisión**: PENDIENTE
- **Aprobador (nombre y rol)**: PENDIENTE (revisor técnico independiente + Dirección Médica)
- **Fecha límite para decidir**: PENDIENTE - antes de F5
- **Fase que bloquea**: F5 (auditoría de login y elevación) y F7 (auditoría clínica)
- **Fecha del borrador**: 2026-10-01

## 1. Contexto

Una auditoría que el administrador de la base puede editar no prueba nada. El Plan v1.2 pide
auditoría pero **no define integridad verificable** (hallazgo A6). Para una HCE, la pregunta
que importa es: *¿se puede demostrar que este registro de acceso no fue alterado después?*

## 2. Criterios

| # | Criterio | Peso |
|---|---|---|
| 1 | Una alteración posterior es **detectable** | Alto |
| 2 | No depende de la buena fe del administrador | Alto |
| 3 | Rendimiento aceptable en escritura | Alto |
| 4 | Verificable por un tercero sin acceso privilegiado | Medio |
| 5 | Operable por un equipo pequeño | Alto |
| 6 | Costo | Medio |

## 3. Opciones

### Opción A: Tabla normal con permisos restringidos
- **Ventajas**: trivial.
- **Desventajas**: el administrador de la base puede modificarla sin dejar rastro.
  **No cumple el criterio 1. Descartada.**

### Opción B: Append-only por permisos + triggers
- `REVOKE UPDATE, DELETE` sobre `audit_events`; trigger que rechaza modificaciones.
- **Ventajas**: simple, rápido, nativo de PostgreSQL.
- **Desventajas**: un superusuario puede quitar el trigger y los permisos. Detectable solo si
  se audita la propia configuración.

### Opción C: Hash encadenado **(recomendada)**
- Cada evento guarda `prev_hash` y `hash = SHA256(prev_hash || contenido_canónico)`.
- Un verificador recorre la cadena y detecta cualquier alteración o borrado intermedio.
- **Ventajas**: la alteración es **matemáticamente detectable**, incluso por el superusuario;
  verificable por un tercero con solo leer; no necesita infraestructura extra.
- **Desventajas**: la escritura debe serializarse por cadena (impacto de rendimiento);
  hay que definir una serialización canónica estable; el verificador debe correr y alguien
  debe mirar su resultado.

### Opción D: C + anclaje externo periódico
- Además de C, el hash de cierre del día se publica fuera del sistema (correo al responsable,
  almacenamiento de solo-escritura).
- **Ventajas**: cierra el último hueco (reescribir **toda** la cadena).
- **Desventajas**: un proceso operativo más que alguien debe sostener.

## 4. Recomendación

**Opción C como base, con B encima** (append-only por permisos *y* hash encadenado: defensa
en profundidad), y **D como mejora** si Dirección Médica lo considera necesario tras la EIPD.

## 5. Decisiones que el ADR fija (si se aprueba)

1. **Qué se audita** (mínimo): acceso a información clínica, cambio sensible, autenticación
   (éxito y fallo), elevación de privilegio, **break-glass**, exportación, merge de pacientes,
   cambio de permisos, alta y baja de usuarios.
2. **Campos**: actor, acción, tipo y **ID técnico** del recurso, momento UTC, correlación,
   resultado, origen (IP/estación), `prev_hash`, `hash`.
3. **Sin PHI**: nunca nombres, documentos, diagnósticos ni texto clínico. Solo IDs.
4. **Serialización canónica**: PENDIENTE definir (orden de campos, codificación, formato de
   fechas). Debe ser estable para siempre; si cambia, la verificación se rompe.
5. **Verificador**: script que recorre la cadena y reporta. Se ejecuta PENDIENTE (propuesta:
   diario, automático) y **alguien recibe el resultado**. Un verificador cuyo informe nadie
   lee no es un control.
6. **Rendimiento**: la escritura de auditoría **no bloquea** la atención. Si la cadena se
   convierte en cuello de botella, se encadena por partición (por día) y se documenta.
7. **Retención**: PENDIENTE - coordinar con ADR-003 §5.
8. **Respaldo**: la auditoría se respalda con el resto y el restore la verifica.

## 6. Consecuencias

- Hay que **ejecutar y mirar** el verificador. Es trabajo operativo recurrente: entra en el
  runbook y en `PROJECT_GOVERNANCE.md`.
- Serializar la escritura tiene un costo; con el volumen de esta IPRESS es previsiblemente
  irrelevante, pero debe **medirse** en F8A, no suponerse.
- Un evento no auditado es invisible para siempre: la lista del punto 1 debe revisarse en
  cada feature.

## 7. Qué debe decidir una persona

| # | Pregunta | Rol | Fecha límite |
|---|---|---|---|
| 1 | ¿C, C+B o C+B+D? | Revisor indep. + Dirección Médica | Antes de F5 |
| 2 | Retención de la auditoría | Asesor legal + Dirección Médica | Antes de F5 |
| 3 | ¿Quién recibe y revisa el informe del verificador, y con qué frecuencia? | Dirección Médica | Antes de F5 |
| 4 | ¿Se audita también la **lectura** de la agenda y de datos de filiación, o solo lo clínico? | Dirección Médica + asesor | Antes de F5 |

## 8. Cómo se revierte

Añadir el encadenamiento después, sobre una auditoría ya existente, deja el periodo anterior
**sin garantía de integridad para siempre**. Debe estar desde el primer evento de F5.
